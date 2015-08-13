require_relative 'common'
require_relative 'git'
require_relative 'credentials'

task :init do

  $git_repo = 'git@github.com:SpaceMadness/lunar-unity-console.git'
  $git_branch = 'develop'

  $dir_temp = File.expand_path 'temp'
  $dir_repo = "#{$dir_temp}/repo"
  $dir_repo_project = "#{$dir_repo}/Project"
  $dir_repo_project_plugin = "#{$dir_repo_project}/Assets/LunarConsole"

  $dir_tools = resolve_path File.expand_path('tools')
  $dir_tools_copyrighter = resolve_path "#{$dir_tools}/copyrighter"

end

task :clean => [:init] do

  FileUtils.rmtree $dir_temp

end

task :clone_repo => [:init] do

  # cleanup
  FileUtils.rmtree $dir_repo

  # clone
  Git.clone $git_repo, $git_branch, $dir_repo
end

task :resolve_version => [:init] do

  def extract_package_version(dir_project)

    file_version = resolve_path "#{dir_project}/Scripts/Constants.cs"
    source = File.read file_version

    source =~ /Version\s+=\s+"(\d+\.\d+.\d+\w?)"/
    return not_nil $1

  end

  $package_version = extract_package_version(resolve_path $dir_repo_project_plugin)
  print_header "Package version: #{$package_version}"

end

task :fix_projects => [:init, :resolve_version] do

  Dir.chdir $dir_repo do

    files = []

    # copyrights
    files = files.concat fix_copyrights(
                             resolve_path($dir_repo),
                             $dir_tools_copyrighter,
                             :types => ['.cs', '.h', '.m', '.mm', '.c', '.cpp', '.java'],
                             :ignored_files => [ 'Plist.cs', 'XCodeEditor-for-Unity', 'SimpleJSON.cs' ]
                         )

    # push changes
    Git.commit_and_push $dir_repo, $git_branch, files if files.length > 0

  end

end


desc 'Release package'
task :release_package => [:clean, :clone_repo, :fix_projects] do

  # call internal builder
  dir_builder = resolve_path "#{$dir_repo}/Builder"

  Dir.chdir dir_builder do
    load File.expand_path 'Rakefile'
    Rake::Task['lunar:export_unity_package'].invoke
  end

  file_package = resolve_path Dir["#{$dir_repo}/Builder/temp/packages/lunar-console-*.unitypackage"].first

  # Merge changes to master
  Git.git_merge $dir_repo, $git_branch, 'master'

  # Create release
  github_create_release $dir_repo, $package_version, file_package

end

def github_create_release(dir_repo, version, package_zip)

  fail_script_unless_file_exists dir_repo
  fail_script_unless_file_exists package_zip

  github_release_bin = resolve_path "#{$dir_tools}/github/github-release"

  Dir.chdir dir_repo do

    name = "SDK v#{version}"
    tag = version

    repo_name = git_get_repo_name '.'
    fail_script_unless repo_name, "Unable to extract repo name: #{dir_repo}"

    # delete old release
    cmd  = %("#{github_release_bin}" delete)
    cmd << %( -s #{$github_access_token})
    cmd << %( -u #{$github_owner})
    cmd << %( -r #{repo_name})
    cmd << %( -t "#{tag}")

    exec_shell cmd, "Can't remove old release", :dont_fail_on_error => true

    # create a release
    release_notes_strings = [ 'Created by buildsystem'] # FIXME!
    release_notes = release_notes_strings.join('')

    cmd  = %("#{github_release_bin}" release)
    cmd << %( -s #{$github_access_token})
    cmd << %( -u #{$github_owner})
    cmd << %( -r #{repo_name})
    cmd << %( -t "#{tag}")
    cmd << %( -n "#{name}")
    cmd << %( -d "#{release_notes}")

    exec_shell cmd, "Can't push release"

    # uploading package
    cmd  = %("#{github_release_bin}" upload)
    cmd << %( -s #{$github_access_token})
    cmd << %( -u #{$github_owner})
    cmd << %( -r #{repo_name})
    cmd << %( -t "#{tag}")
    cmd << %( -n "#{File.basename(package_zip)}")
    cmd << %( -f "#{File.expand_path(package_zip)}")

    exec_shell cmd, "Can't upload package asset"

  end
end

############################################################

def git_get_repo_name(dir_repo)
  Dir.chdir dir_repo do
    file_config = '.git/config'
    config = File.read file_config
    return extract_regex config, %r#url = git@github\.com:.*?/(.*?).git#
  end
end

############################################################

def get_release_notes(dir_repo, version)
  Dir.chdir dir_repo do
    file_release_notes = 'CHANGELOG.md'
    fail_script_unless_file_exists file_release_notes

    lines = File.readlines file_release_notes
    notes = []

    block_found = false
    lines.each { |line|

      if (block_found)
        if (line.start_with? '*')
          notes.push line
        elsif line.start_with? '##'
          break
        end
      elsif line.start_with? "## v#{version}"
        block_found = true
      end
    }

    return notes
  end
end


