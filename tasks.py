import os
import re
import shutil
from invoke import task
from pathlib import Path

from common import resolve_path, not_nil, print_header, exec_shell, join_path, find_in_file, fix_copyrights
from git_repo import GitRepo
from unity_project import UnityProject
from build_platform import BuildPlatform

@task
def init(c):
    # Store values directly in context instead of global dict
    c.publish_unity = resolve_path(BuildPlatform.unity_publish_binary())
    c.git_repo = "https://github.com/SpaceMadness/lunar-unity-console.git"
    c.git_branch = "develop"
    c.git_repo_publisher = "https://github.com/SpaceMadness/lunar-unity-console-publisher.git"
    c.git_branch_publisher = "master"
    c.dir_temp = Path("temp").resolve()
    c.dir_packages = Path("temp/packages").resolve()
    c.dir_publisher = Path("temp/publisher").resolve()
    c.dir_samples = Path("temp/samples").resolve()
    c.dir_repo = Path("temp/repo").resolve()
    c.dir_test_project = Path("TestProject").resolve()
    c.dir_repo_project = Path("temp/repo/Project").resolve()
    c.dir_repo_project_plugin = Path("temp/repo/Project/Assets/LunarConsole").resolve()
    c.dir_tools = resolve_path("tools")
    c.dir_tools_copyrighter = resolve_path("tools/copyrighter")

@task(init)
def clean(c):
    shutil.rmtree(c.dir_temp, ignore_errors=True)

@task
def _free(c):
    c.plugin_configuration = "free"

@task
def _full(c):
    c.plugin_configuration = "full"

@task(init)
def _clone_repo(c):
    git_repo = not_nil(c.git_repo)
    git_branch = not_nil(c.git_branch)
    dir_repo = not_nil(c.dir_repo)
    
    shutil.rmtree(dir_repo, ignore_errors=True)

    print_header(f"Cloning repository: {git_repo} ({git_branch})")
    exec_shell(f"git clone --depth 1 --branch {git_branch} {git_repo} {dir_repo}", "Can't clone repository")


@task(init)
def _resolve_version(c):
    def extract_package_version(path):
        file_path = join_path(path, "Scripts", "Constants.cs")
        return not_nil(find_in_file(file_path, pattern=r'Version = "([^"]+);"'))

    dir_project = resolve_path(c.dir_repo_project_plugin)
    c.package_version = extract_package_version(dir_project)
    print_header(f"Package version: {c.package_version}")

@task(init, _resolve_version)
def _fix_projects(c):
    files = []

    files.extend(
        fix_copyrights(
            c.dir_repo,
            c.dir_tools_copyrighter,
            types=[".cs", ".h", ".m", ".mm", ".c", ".cpp", ".java"],
            ignored_files=["Plist.cs", "XCodeEditor-for-Unity", "SimpleJSON.cs"]
        )
    )

    if files:
        repo = GitRepo(c.dir_repo)
        repo.add_files(files)
        repo.commit("Updated copyrights")
        repo.push(c.git_branch)

@task(init)
def build_package_no_clean(c):
    dir_builder = c.dir_repo / "Builder"

    invoke_task = f"export-unity-package-{c.plugin_configuration}"
    exec_shell(f"invoke {invoke_task}", working_dir=dir_builder)

    file_package = next((dir_builder / "temp/packages").glob("lunar-console-*.unitypackage"), None)
    c.dir_packages.mkdir(parents=True, exist_ok=True)
    shutil.copy(file_package, c.dir_packages)

@task(clean, _clone_repo, _fix_projects, build_package_no_clean)
def build_package(c):
    pass

@task(init)
def clean_test_project(c):
    print_header("Clean up project...")
    os.chdir(c.dir_test_project)
    exec_shell('git clean -x -f -d', "Can't clean project")
    exec_shell(f'git checkout -- "{c.dir_test_project}"', "Can't reset project")

@task(clean_test_project)
def prepare_test_project(c):
    file_package = next(c.dir_packages.glob("lunar-console-*.unitypackage"), None)
    project = UnityProject(c.dir_test_project)

    print_header("Importing package...")
    project.import_package(file_package)

    print_header("Integrating package...")
    project.exec_unity_method("LunarConsoleBuilder.Builder.IntegratePlugin")

    print_header("Enabling package...")
    project.exec_unity_method("LunarConsoleEditorInternal.Installer.EnablePlugin")

@task(build_package, prepare_test_project)
def build_test_project(c):
    project = UnityProject(c.dir_test_project)

    print_header("Exporting apps...")
    project.exec_unity_method("LunarConsoleBuilder.Builder.BuildAll")

    ios_app = build_ios_app(c.dir_test_project / "Build/iOS", "Unity-iPhone", "Release", "Unity-iPhone")
    android_app = next((c.dir_test_project / "Build/Android").glob("*.apk"), None)

    c.dir_samples.mkdir(parents=True, exist_ok=True)
    shutil.copy(ios_app, c.dir_samples)
    shutil.copy(android_app, c.dir_samples)

@task(build_package)
def prepare_publisher_project(c):
    package = next(c.dir_packages.glob("lunar-console-*.unitypackage"), None)

    print_header("Cloning publisher project...")
    GitRepo.clone(c.git_repo_publisher, c.git_branch_publisher, c.dir_publisher)

    project = UnityProject(c.dir_publisher, c.publish_unity)
    project.import_package(package)

    readme_src = Path("package_readme.txt").resolve()
    readme_dst = c.dir_publisher / "Assets/LunarConsole/readme.txt"
    shutil.copy(readme_src, readme_dst)

    project.open()

@task(pre=[_free, prepare_publisher_project])
def _prepare_publisher_project_free(c):
    print("Publisher project prepared for FREE release.")

@task(pre=[_full, prepare_publisher_project])
def _prepare_publisher_project_full(c):
    print("Publisher project prepared for FULL release.")

@task(pre=[_free])
def release_package(c):
    print("Building package for release...")
    # Replace these variables with appropriate values
    builder_dir_packages = "path_to_packages"
    builder_dir_repo = "path_to_repo"
    builder_git_branch = "source_branch"
    package_version = "1.0.0"

    # Resolve package file
    file_package = resolve_path(os.path.join(builder_dir_packages, "lunar-console-*.unitypackage"))
    if not file_package:
        print("Error: Package file not found.")
        return

    # Merge changes to master
    git_merge(builder_dir_repo, builder_git_branch, "master")

    # Create release
    github_create_release(builder_dir_repo, package_version, file_package)

    print("Release package task completed.")


def git_get_repo_name(dir_repo):
    os.chdir(dir_repo)
    file_config = '.git/config'

    with open(file_config, 'r') as file:
        config = file.read()

    match = re.search(r'url = git@github\.com:.*?/(.*?).git', config)
    if match:
        return match.group(1)
    return None