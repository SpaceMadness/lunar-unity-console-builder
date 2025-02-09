from github import Github, Repository
import re
import os

from git_repo import GitRepo


class GitHub:
    def __init__(self, access_token):
        self.client = Github(access_token)

    @staticmethod
    def get_repo_url(dir_repo):
        # Assuming `GitRepo` is replaced with a method to get the repo URL
        repo_url = GitRepo(dir_repo).repo_url
        return repo_url.rstrip(".git") if repo_url.endswith(".git") else repo_url

    def create_pull_request(self, dir_repo, base, head, title, body):
        repo_url = self.get_repo_url(dir_repo)
        repo = self.client.get_repo(repo_url)
        repo.create_pull(title=title, body=body, base=base, head=head)

    def create_release(self, dir_repo, tag, title, body, artifact=None):
        if artifact and not os.path.exists(artifact):
            raise FileNotFoundError(f"Artifact file not found: {artifact}")

        repo_url = self.get_repo_url(dir_repo)
        repo = self.client.get_repo(repo_url)

        release = repo.create_git_release(tag=tag, name=title, message=body, draft=True)

        if artifact:
            with open(artifact, "rb") as file:
                release.upload_asset(file, content_type="application/gzip")

    def get_latest_release(self, git_repo):
        releases = self.list_releases(git_repo)
        return releases[0] if releases else None

    def list_releases(self, git_repo):
        repo = self.client.get_repo(git_repo)
        releases = repo.get_releases()

        sorted_releases = sorted(
            releases,
            key=lambda release: self.extract_version_from_tag(release.tag_name),
            reverse=True,
        )

        if not sorted_releases:
            raise ValueError("Can't resolve GitHub releases")

        return sorted_releases

    @staticmethod
    def extract_version_from_tag(tag):
        match = re.search(r"(\d+\.\d+(\.\d+)?)", tag)
        if not match:
            raise ValueError(f"Invalid tag format: {tag}")
        return match.group(1)


# Example usage
# Replace with your GitHub access token and other details
GITHUB_ACCESS_TOKEN = "your_github_access_token_here"
github_helper = GitHub(GITHUB_ACCESS_TOKEN)

# Example function calls
# github_helper.create_pull_request(dir_repo="repo_dir", base="main", head="feature-branch", title="PR Title", body="PR Body")
# github_helper.create_release(dir_repo="repo_dir", tag="v1.0.0", title="Release Title", body="Release Body", artifact="path/to/artifact.tar.gz")
# latest_release = github_helper.get_latest_release("repo_name")
# print(latest_release)
