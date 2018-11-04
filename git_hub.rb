require 'octokit'
require_relative 'git_repo'
require_relative 'credentials'

class GitHub
  # @param [String] dir_repo
  # @param [String] base
  # @param [String] head
  # @param [String] title
  # @param [String] body
  def self.create_pull_request(dir_repo, base, head, title, body)
    repo_url = GitRepo.new(dir_repo).repo_url
    repo_url = repo_url.chomp '.git' if repo_url.end_with? '.git'

    repo = Octokit::Repository.from_url repo_url
    client = Octokit::Client.new
    client.access_token = $github_access_token
    client.create_pull_request repo, base, head, title, body
  end

  def self.create_release(dir_repo, tag, title, body, artifact = nil)
    fail_script_unless_file_exists artifact unless artifact.nil?

    repo_url = GitRepo.new(dir_repo).repo_url
    repo_url = repo_url.chomp '.git' if repo_url.end_with? '.git'

    repo = Octokit::Repository.from_url repo_url
    client = Octokit::Client.new
    client.access_token = $github_access_token
    release = client.create_release repo, tag, name: title, body: body, draft: true
    unless artifact.nil?
      client.upload_asset release.url, artifact, content_type: 'application/gzip'
    end
  end

  def self.get_latest_release(git_repo)
    releases = list_releases git_repo
    releases.first
  end

  def self.list_releases(git_repo)
    repo = Octokit::Repository.from_url git_repo
    client = Octokit::Client.new
    comparator = lambda { |a, b|
      Gem::Version.new(extract_version_from_tag(b.tag_name)) <=> Gem::Version.new(extract_version_from_tag(a.tag_name))
    }
    releases = client.releases(repo).sort(&comparator)
    fail_script_if releases.empty?, "Can't resolve Github releases"

    releases
  end

  def self.extract_version_from_tag(tag)
    tag =~ /(\d+\.\d+(.\d+)?)/
    not_nil $1
  end
end