require 'fileutils'

require_relative 'common'
require_relative 'git'
require_relative 'credentials'
require_relative 'unity_project'

task :init do

  $bin_release_unity = resolve_path '/Applications/Unity5/Unity.app/Contents/MacOS/Unity'

  $git_repo = 'git@github.com:SpaceMadness/lunar-unity-console.git'
  $git_branch = 'develop'

  $git_repo_publisher = 'git@github.com:SpaceMadness/lunar-unity-console-publisher.git'
  $git_branch_publisher = 'master'

  $dir_temp = File.expand_path 'temp'
  $dir_packages = "#{$dir_temp}/packages"
  $dir_publisher = "#{$dir_temp}/publisher"
  $dir_samples = "#{$dir_temp}/samples"
  $dir_repo = "#{$dir_temp}/repo"

  $dir_test_project = File.expand_path 'TestProject'

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

desc 'Build package on existing source'
task :build_package_no_clean => [:init] do

  # call internal builder
  dir_builder = resolve_path "#{$dir_repo}/Builder"

  Dir.chdir dir_builder do
    load File.expand_path 'Rakefile'
    Rake::Task['lunar:export_unity_package'].invoke
  end

  file_package = resolve_path Dir["#{$dir_repo}/Builder/temp/packages/lunar-console-*.unitypackage"].first
  FileUtils.rm_rf $dir_packages
  FileUtils.makedirs $dir_packages

  FileUtils.cp file_package, "#{$dir_packages}/"

end

desc 'Build package'
task :build_package => [:clean, :clone_repo, :fix_projects, :build_package_no_clean] do
end

desc 'Clean up test project'
task :clean_test_project => [:init] do

  print_header 'Clean up project...'
  Dir.chdir $dir_test_project do
    exec_shell 'git clean -x -f -d', "Can't clean project"
  end
  exec_shell "git checkout -- \"#{$dir_test_project}\"", "Can't reset project"

end

desc 'Prepare test project'
task :prepare_test_project => [:clean_test_project] do

  file_package = resolve_path Dir["#{$dir_packages}/lunar-console-*.unitypackage"].first

  project = UnityProject.new $dir_test_project

  print_header 'Importing package...'
  project.import_package file_package

  print_header 'Integrating package...'
  project.exec_unity_method 'LunarConsoleBuilder.Builder.IntegratePlugin'

  print_header 'Enabling package...'
  project.exec_unity_method 'LunarConsoleInternal.Installer.EnablePlugin'

  print_header 'Exporting apps...'
  project.exec_unity_method 'LunarConsoleBuilder.Builder.BuildAll'

end

desc 'Builds test project'
task :build_test_project => [:build_package, :prepare_test_project] do

  ios_app = build_ios_app "#{$dir_test_project}/Build/iOS", 'Unity-iPhone', 'Release', 'Unity-iPhone'
  fail_script_unless_file_exists ios_app

  FileUtils.rm_rf $dir_samples
  FileUtils.mkpath $dir_samples

  FileUtils.cp_r ios_app, "#{$dir_samples}/"

end

desc 'Prepares publisher project'
task :prepare_publisher_project => [:build_package] do

  package = resolve_path Dir["#{$dir_packages}/lunar-console-*.unitypackage"].first

  print_header 'Cloning publisher project...'
  Git.clone $git_repo_publisher, $git_branch_publisher, $dir_publisher

  print_header 'Preparing publisher project...'

  # import plugin package
  project = UnityProject.new $dir_publisher, $bin_release_unity
  project.import_package package

  # copy readme
  readme_src = resolve_path 'package_readme.txt'
  readme_dst = "#{$dir_publisher}/Assets/LunarConsole/readme.txt"

  FileUtils.cp readme_src, readme_dst

  project.open

end

desc 'Release package'
task :release_package => [:build_package] do

  file_package = resolve_path Dir["#{$dir_packages}/lunar-console-*.unitypackage"].first

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

    name = "Lunar Console v#{version}"
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
    release_notes = get_release_notes dir_repo, version

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


