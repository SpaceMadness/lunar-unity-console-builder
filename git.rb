require_relative 'common.rb'

module Builder

  class Git

    def self.clone(repo, branch, dest_dir)

      exec_shell("git clone #{repo} --depth 1 -b #{branch} #{dest_dir}", "Can't clone repo: #{repo}")

      Dir.chdir dest_dir do
        exec_shell('git submodule init', "Can't init git submodules")
        exec_shell('git submodule update', "Can't update git submodules")
      end
    end

    def self.commit_and_push(repo, branch, files)

      Dir.chdir repo do
        files.each { |file|
          exec_shell %(git add "#{file}"), "Can't add file: #{file}"
        }
        exec_shell 'git commit -m "Project fixes: versions, copyrights, etc" --author "Space Cadet Stimpy <a.lementuev+cadet+stimpy@gmail.com>"', "Can't commit to git"
        exec_shell %(git push origin #{branch}), "Can't push to git"
      end

    end

    def self.git_merge(dir_repo, from_branch, to_branch, message = nil)
      message = %(Merged branch '#{from_branch}' into #{to_branch}) if message == nil
      Dir.chdir dir_repo do
        exec_shell(%(git branch #{to_branch} --force), "Can't switch a branch '#{to_branch}")
        exec_shell(%(git merge #{from_branch} -X ours -m "#{message}"), "Can't merge a branch")
        exec_shell("git push origin #{to_branch} --force", "Can't push branch to remote")
      end
    end

  end

end