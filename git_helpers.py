import shutil

from common import print_header, exec_shell


def git_clone(dest_dir: str, git_branch: str, git_repo: str):
    shutil.rmtree(dest_dir, ignore_errors=True)
    print_header(f"Cloning repository: {git_repo} ({git_branch})")
    exec_shell(f"git clone --depth 1 --branch {git_branch} {git_repo} {dest_dir}", "Can't clone repository")
