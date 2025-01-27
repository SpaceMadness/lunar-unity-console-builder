import os
import re
import shutil
from invoke import task
from pathlib import Path

# Mock imports for required modules
# These need to be implemented or replaced with the actual Python equivalents.
from common import resolve_path, not_nil, print_header, exec_shell
from git_hub import GitHub
from git_repo import GitRepo
from unity_project import UnityProject
from platform import Platform

@task
def init(c):
    global builder_vars
    builder_vars = {
        "publish_unity": resolve_path(Platform.unity_publish),
        "git_repo": "https://github.com/SpaceMadness/lunar-unity-console.git",
        "git_branch": "develop",
        "git_repo_publisher": "https://github.com/SpaceMadness/lunar-unity-console-publisher.git",
        "git_branch_publisher": "master",
        "dir_temp": Path("temp").resolve(),
        "dir_packages": Path("temp/packages").resolve(),
        "dir_publisher": Path("temp/publisher").resolve(),
        "dir_samples": Path("temp/samples").resolve(),
        "dir_repo": Path("temp/repo").resolve(),
        "dir_test_project": Path("TestProject").resolve(),
        "dir_repo_project": Path("temp/repo/Project").resolve(),
        "dir_repo_project_plugin": Path("temp/repo/Project/Assets/LunarConsole").resolve(),
        "dir_tools": resolve_path("tools"),
        "dir_tools_copyrighter": resolve_path("tools/copyrighter"),
    }

@task(init)
def clean(c):
    shutil.rmtree(builder_vars["dir_temp"], ignore_errors=True)

@task
def free(c):
    global plugin_configuration
    plugin_configuration = "free"

@task
def full(c):
    global plugin_configuration
    plugin_configuration = "full"

@task(init)
def clone_repo(c):
    shutil.rmtree(builder_vars["dir_repo"], ignore_errors=True)
    GitRepo.clone(builder_vars["git_repo"], builder_vars["git_branch"], builder_vars["dir_repo"])

@task(init)
def resolve_version(c):
    def extract_package_version(dir_project):
        file_version = dir_project / "Scripts/Constants.cs"
        source = file_version.read_text()
        version = not_nil(source.split('Version = "', 1)[-1].split('"', 1)[0])
        return version

    builder_vars["package_version"] = extract_package_version(builder_vars["dir_repo_project_plugin"])
    print_header(f"Package version: {builder_vars['package_version']}")

@task(init, resolve_version)
def fix_projects(c):
    os.chdir(builder_vars["dir_repo"])
    files = []

    files.extend(
        fix_copyrights(
            builder_vars["dir_repo"],
            builder_vars["dir_tools_copyrighter"],
            types=[".cs", ".h", ".m", ".mm", ".c", ".cpp", ".java"],
            ignored_files=["Plist.cs", "XCodeEditor-for-Unity", "SimpleJSON.cs"]
        )
    )

    if files:
        GitRepo.commit_and_push(builder_vars["dir_repo"], builder_vars["git_branch"], "Updated copyrights", files)

@task(init)
def build_package_no_clean(c):
    dir_builder = builder_vars["dir_repo"] / "Builder"
    os.chdir(dir_builder)

    # Assuming Rake tasks are replaced with equivalent Python commands
    invoke_task = f"lunar:export_unity_package_{plugin_configuration}"
    exec_shell(f"invoke {invoke_task}")

    file_package = next((dir_builder / "temp/packages").glob("lunar-console-*.unitypackage"), None)
    builder_vars["dir_packages"].mkdir(parents=True, exist_ok=True)
    shutil.copy(file_package, builder_vars["dir_packages"])

@task(clean, clone_repo, fix_projects, build_package_no_clean)
def build_package(c):
    pass

@task(init)
def clean_test_project(c):
    print_header("Clean up project...")
    os.chdir(builder_vars["dir_test_project"])
    exec_shell('git clean -x -f -d', "Can't clean project")
    exec_shell(f'git checkout -- "{builder_vars["dir_test_project"]}"', "Can't reset project")

@task(clean_test_project)
def prepare_test_project(c):
    file_package = next(builder_vars["dir_packages"].glob("lunar-console-*.unitypackage"), None)
    project = UnityProject(builder_vars["dir_test_project"])

    print_header("Importing package...")
    project.import_package(file_package)

    print_header("Integrating package...")
    project.exec_unity_method("LunarConsoleBuilder.Builder.IntegratePlugin")

    print_header("Enabling package...")
    project.exec_unity_method("LunarConsoleEditorInternal.Installer.EnablePlugin")

@task(build_package, prepare_test_project)
def build_test_project(c):
    project = UnityProject(builder_vars["dir_test_project"])

    print_header("Exporting apps...")
    project.exec_unity_method("LunarConsoleBuilder.Builder.BuildAll")

    ios_app = build_ios_app(builder_vars["dir_test_project"] / "Build/iOS", "Unity-iPhone", "Release", "Unity-iPhone")
    android_app = next((builder_vars["dir_test_project"] / "Build/Android").glob("*.apk"), None)

    builder_vars["dir_samples"].mkdir(parents=True, exist_ok=True)
    shutil.copy(ios_app, builder_vars["dir_samples"])
    shutil.copy(android_app, builder_vars["dir_samples"])

@task(build_package)
def prepare_publisher_project(c):
    package = next(builder_vars["dir_packages"].glob("lunar-console-*.unitypackage"), None)

    print_header("Cloning publisher project...")
    GitRepo.clone(builder_vars["git_repo_publisher"], builder_vars["git_branch_publisher"], builder_vars["dir_publisher"])

    project = UnityProject(builder_vars["dir_publisher"], builder_vars["publish_unity"])
    project.import_package(package)

    readme_src = Path("package_readme.txt").resolve()
    readme_dst = builder_vars["dir_publisher"] / "Assets/LunarConsole/readme.txt"
    shutil.copy(readme_src, readme_dst)

    project.open()

@task(pre=[free, prepare_publisher_project])
def prepare_publisher_project_free(c):
    print("Publisher project prepared for FREE release.")

@task(pre=[full, prepare_publisher_project])
def prepare_publisher_project_full(c):
    print("Publisher project prepared for FULL release.")

@task(pre=[free])
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