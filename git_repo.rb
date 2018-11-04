require_relative 'common'

require 'git'

class GitRepo
  class Remote
    attr_reader :url, :name

    def initialize(name, url)
      @name = name
      @url = url
    end

    def to_s
      "#{@name}: #{@url}"
    end
  end

  def initialize(working_copy)
    @git = Git.open resolve_path(working_copy)
  end

  # clones git repo
  def self.clone(repository, branch, dest_dir)
    dest_dir_abs = File.expand_path(dest_dir)
    delete_file dest_dir_abs
    path = File.dirname dest_dir_abs
    name = File.basename dest_dir_abs
    print_progress "Cloning #{repository} (#{branch}) into #{dest_dir_abs}"
    Git.clone repository, name, branch: branch, path: path
    GitRepo.new dest_dir_abs
  end

  def checkout_branch(branch_name)
    branch = @git.branch branch_name
    branch.checkout
    fail_script_unless branch_name == current_branch, "Failed to create branch '#{branch_name}'"
  end

  def current_branch
    @git.current_branch
  end

  def list_changed_files
    names = []
    names.push *(@git.status.changed.keys)
    names.push *(@git.status.deleted.keys)
    names.push *(@git.status.untracked.keys)
    names.sort
  end

  def add_files(files)
    @git.add files
  end

  def commit(message, options = {})
    if options[:all]
      @git.commit_all message
    else
      @git.commit message
    end
  end

  def tag(name)
    @git.add_tag name
  end

  def push(branch = nil, options = {})
    branch = @git.current_branch if branch.nil?
    @git.push 'origin', branch, options
  end

  def merge(source_branch, target_branch)
    @git.checkout target_branch
    @git.merge source_branch, "Merged '#{source_branch}' into '#{target_branch}'"
  end

  def list_remotes
    remotes = []
    @git.remotes.each do |remote|
      remotes << Remote.new(remote.name, remote.url)
    end
    remotes
  end

  def repo_url
    remotes = list_remotes
    fail_script_if remotes.empty?, "Can't get repo url: no remotes"
    fail_script_if remotes.length != 1, "Can't get repo url: multiple remotes defined"
    remotes[0].url
  end

  def self.git_merge(dir_repo, from_branch, to_branch, message = nil)
    message = %(Merged branch '#{from_branch}' into #{to_branch}) if message.nil?
    Dir.chdir dir_repo do
      exec_shell(%(git branch #{to_branch} --force), "Can't switch a branch '#{to_branch}")
      exec_shell(%(git merge #{from_branch} -X ours -m "#{message}"), "Can't merge a branch")
      exec_shell("git push origin #{to_branch} --force", "Can't push branch to remote")
    end
  end
end