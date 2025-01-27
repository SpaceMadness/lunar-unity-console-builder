import os
import shutil
from git import Repo, GitCommandError


class GitRepo:
    class Remote:
        def __init__(self, name, url):
            self.name = name
            self.url = url

        def __str__(self):
            return f"{self.name}: {self.url}"

    def __init__(self, working_copy):
        self.repo = Repo(os.path.abspath(working_copy))

    @staticmethod
    def clone(repository, branch, dest_dir):
        dest_dir_abs = os.path.abspath(dest_dir)
        if os.path.exists(dest_dir_abs):
            shutil.rmtree(dest_dir_abs)
        parent_dir = os.path.dirname(dest_dir_abs)
        repo_name = os.path.basename(dest_dir_abs)
        print(f"Cloning {repository} ({branch}) into {dest_dir_abs}")
        Repo.clone_from(repository, os.path.join(parent_dir, repo_name), branch=branch)
        return GitRepo(dest_dir_abs)

    def checkout_branch(self, branch_name):
        branch = self.repo.heads[branch_name] if branch_name in self.repo.heads else self.repo.create_head(branch_name)
        branch.checkout()
        if branch_name != self.current_branch():
            raise RuntimeError(f"Failed to create branch '{branch_name}'")

    def current_branch(self):
        return self.repo.active_branch.name

    def list_changed_files(self):
        status = self.repo.git.status("--porcelain").splitlines()
        changed_files = [line[3:] for line in status]
        return sorted(changed_files)

    def add_files(self, files):
        self.repo.index.add(files)

    def commit(self, message, all_files=False):
        if all_files:
            self.repo.git.add(A=True)
        self.repo.index.commit(message)

    def tag(self, name):
        self.repo.create_tag(name)

    def push(self, branch=None, options=None):
        if branch is None:
            branch = self.current_branch()
        try:
            self.repo.git.push("origin", branch, **(options or {}))
        except GitCommandError as e:
            print(f"Failed to push branch '{branch}': {e}")

    def merge(self, source_branch, target_branch):
        self.checkout_branch(target_branch)
        self.repo.git.merge(source_branch, f"Merged '{source_branch}' into '{target_branch}'")

    def list_remotes(self):
        remotes = []
        for remote in self.repo.remotes:
            remotes.append(self.Remote(remote.name, remote.url))
        return remotes

    def repo_url(self):
        remotes = self.list_remotes()
        if not remotes:
            raise RuntimeError("Can't get repo URL: no remotes")
        if len(remotes) != 1:
            raise RuntimeError("Can't get repo URL: multiple remotes defined")
        return remotes[0].url

    @staticmethod
    def git_merge(dir_repo, from_branch, to_branch, message=None):
        if message is None:
            message = f"Merged branch '{from_branch}' into {to_branch}"
        os.chdir(dir_repo)
        os.system(f"git branch {to_branch} --force")
        os.system(f"git merge {from_branch} -X ours -m \"{message}\"")
        os.system(f"git push origin {to_branch} --force")

    @staticmethod
    def commit_and_push(dir_repo, git_branch, message, files):
        repo = GitRepo(dir_repo)
        repo.add_files(files)
        repo.commit(message)
        repo.push(git_branch)
