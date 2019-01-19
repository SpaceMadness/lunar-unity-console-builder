require 'fileutils'

require_relative 'common'
require_relative 'git_hub'
require_relative 'git_repo'
require_relative 'credentials'
require_relative 'unity_project'
require_relative 'platform'

include Builder

namespace :builder do

  task :init do

    $builder_publish_unity = resolve_path Platform.unity_publish

    $builder_git_repo = 'https://github.com/SpaceMadness/lunar-unity-console.git'
    $builder_git_branch = 'develop'

    $builder_git_repo_publisher = 'https://github.com/SpaceMadness/lunar-unity-console-publisher.git'
    $builder_git_branch_publisher = 'master'

    $builder_dir_temp = File.expand_path 'temp'
    $builder_dir_packages = "#{$builder_dir_temp}/packages"
    $builder_dir_publisher = "#{$builder_dir_temp}/publisher"
    $builder_dir_samples = "#{$builder_dir_temp}/samples"
    $builder_dir_repo = "#{$builder_dir_temp}/repo"

    $builder_dir_test_project = File.expand_path 'TestProject'

    $builder_dir_repo_project = "#{$builder_dir_repo}/Project"
    $builder_dir_repo_project_plugin = "#{$builder_dir_repo_project}/Assets/LunarConsole"

    $builder_dir_tools = resolve_path File.expand_path('tools')
    $builder_dir_tools_copyrighter = resolve_path "#{$builder_dir_tools}/copyrighter"

  end

  task :clean => [:init] do
    FileUtils.rmtree $builder_dir_temp
  end

  task :free  do
    $plugin_configuration = 'free'
  end

  task :full  do
    $plugin_configuration = 'full'
  end

  task :clone_repo => [:init] do

    # cleanup
    FileUtils.rmtree $builder_dir_repo

    # clone
    GitRepo.clone $builder_git_repo, $builder_git_branch, $builder_dir_repo
  end

  task :resolve_version => [:init] do

    def extract_package_version(dir_project)

      file_version = resolve_path "#{dir_project}/Scripts/Constants.cs"
      source = File.read file_version

      source =~ /Version\s+=\s+"(\d+\.\d+.\d+\w?)"/
      return not_nil $1

    end

    $package_version = extract_package_version(resolve_path $builder_dir_repo_project_plugin)
    print_header "Package version: #{$package_version}"

  end

  task :fix_projects => [:init, :resolve_version] do

    Dir.chdir $builder_dir_repo do

      files = []

      # copyrights
      files = files.concat fix_copyrights(
                               resolve_path($builder_dir_repo),
                               $builder_dir_tools_copyrighter,
                               :types => ['.cs', '.h', '.m', '.mm', '.c', '.cpp', '.java'],
                               :ignored_files => [ 'Plist.cs', 'XCodeEditor-for-Unity', 'SimpleJSON.cs' ]
                           )

      # push changes
      GitRepo.commit_and_push($builder_dir_repo, $builder_git_branch, "Updated copyrights", files) if files.length > 0

    end

  end

  desc 'Build package on existing source'
  task :build_package_no_clean => [:init] do

    # call internal builder
    dir_builder = resolve_path "#{$builder_dir_repo}/Builder"

    Dir.chdir dir_builder do
      load File.expand_path 'Rakefile'
      Rake::Task["lunar:export_unity_package_#{$plugin_configuration}"].invoke
    end

    file_package = resolve_path Dir["#{$builder_dir_repo}/Builder/temp/packages/lunar-console-*.unitypackage"].first
    FileUtils.rm_rf $builder_dir_packages
    FileUtils.makedirs $builder_dir_packages

    FileUtils.cp file_package, "#{$builder_dir_packages}/"

  end

  task :build_package => [:clean, :clone_repo, :fix_projects, :build_package_no_clean]

  desc 'Clean up test project'
  task :clean_test_project => [:init] do

    print_header 'Clean up project...'
    Dir.chdir $builder_dir_test_project do
      exec_shell 'git clean -x -f -d', "Can't clean project"
    end
    exec_shell "git checkout -- \"#{$builder_dir_test_project}\"", "Can't reset project"

  end

  desc 'Prepare test project'
  task :prepare_test_project => [:clean_test_project] do

    file_package = resolve_path Dir["#{$builder_dir_packages}/lunar-console-*.unitypackage"].first

    project = UnityProject.new $builder_dir_test_project

    print_header 'Importing package...'
    project.import_package file_package

    print_header 'Integrating package...'
    project.exec_unity_method 'LunarConsoleBuilder.Builder.IntegratePlugin'

    print_header 'Enabling package...'
    project.exec_unity_method 'LunarConsoleEditorInternal.Installer.EnablePlugin'

  end

  desc 'Builds test project'
  task :build_test_project => [:build_package, :prepare_test_project] do

    project = UnityProject.new $builder_dir_test_project

    print_header 'Exporting apps...'
    project.exec_unity_method 'LunarConsoleBuilder.Builder.BuildAll'

    ios_app = resolve_path build_ios_app("#{$builder_dir_test_project}/Build/iOS", 'Unity-iPhone', 'Release', 'Unity-iPhone')
    android_app = resolve_path Dir["#{$builder_dir_test_project}/Build/Android/*.apk"].first

    FileUtils.rm_rf $builder_dir_samples
    FileUtils.mkpath $builder_dir_samples

    FileUtils.cp_r ios_app, "#{$builder_dir_samples}/"
    FileUtils.cp_r android_app, "#{$builder_dir_samples}/"

  end

  task :prepare_publisher_project => [:build_package] do

    package = resolve_path Dir["#{$builder_dir_packages}/lunar-console-*.unitypackage"].first

    print_header 'Cloning publisher project...'
    GitRepo.clone $builder_git_repo_publisher, $builder_git_branch_publisher, $builder_dir_publisher

    print_header 'Preparing publisher project...'

    # import plugin package
    project = UnityProject.new $builder_dir_publisher, $builder_publish_unity
    project.import_package package

    # copy readme
    readme_src = resolve_path 'package_readme.txt'
    readme_dst = "#{$builder_dir_publisher}/Assets/LunarConsole/readme.txt"

    FileUtils.cp readme_src, readme_dst

    project.open

  end

  desc 'Prepares publisher project for FREE release'
  task :prepare_publisher_project_free => [:free, :prepare_publisher_project]

  desc 'Prepares publisher project for FULL release'
  task :prepare_publisher_project_full => [:full, :prepare_publisher_project]

  desc 'Release package'
  task :release_package => [:free, :build_package] do

    file_package = resolve_path Dir["#{$builder_dir_packages}/lunar-console-*.unitypackage"].first

    # Merge changes to master
    GitRepo.git_merge $builder_dir_repo, $builder_git_branch, 'master'

    # Create release
    github_create_release $builder_dir_repo, $package_version, file_package

  end

  def github_create_release(dir_repo, version, package_zip)

    fail_script_unless_file_exists dir_repo
    fail_script_unless_file_exists package_zip

    # extracting changelog
    release_notes = get_release_notes dir_repo, @version

    # preparing release commit
    repo = GitRepo.new dir_repo
    release_name = "Lunar Console v#{version}"

    release_tag = version
    print_header 'Creating release tag...'
    repo.tag release_tag
    repo.push 'master', tags: true

    # creating pull request
    print_header 'Creating draft GitHub release...'
    GitHub.create_release dir_repo, release_tag, release_name, release_notes, File.expand_path(package_zip)
  end

  ############################################################

  def git_get_repo_name(dir_repo)
    Dir.chdir dir_repo do
      file_config = '.git/config'
      config = File.read file_config
      return extract_regex config, %r#url = git@github\.com:.*?/(.*?).git#
    end
  end

end


