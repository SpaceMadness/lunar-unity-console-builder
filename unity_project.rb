require_relative 'common.rb'

module Builder

  class UnityProject

    attr_reader :dir_project

    def initialize(dir_project, bin_unity = '/Applications/Unity/Unity.app/Contents/MacOS/Unity') # Windows support? Nah!
      @dir_project = resolve_path File.expand_path(dir_project)
      @bin_unity   = resolve_path bin_unity
    end

    def exec_unity_method(method, args = {}, error_message = nil)
      exec_unity_method_opt @dir_project, method, args, {}, error_message
    end

    def exec_unity_method_opt(project, method, args = {}, options = {}, error_message = nil)

      cmd = %("#{@bin_unity}")
      cmd << ' -quit' unless options.has_key? :no_quit
      cmd << ' -batchmode' unless options.has_key? :no_batch
      cmd << %( "#{make_custom_args(args)}") if args != nil && args.length > 0
      cmd << " -executeMethod #{method}"
      cmd << %( -projectPath "#{project}")

      exec_shell cmd, error_message.nil? ? "Can't execute method: #{method}\nProject: #{project}" : error_message

      unity_log = File.expand_path '~/Library/Logs/Unity/Editor.log'
      fail_script_unless_file_exists unity_log

      result = File.read unity_log
      result =~ /(Exiting batchmode successfully now!)/

      fail_script_unless $1 != nil, "Unity batch failed\n#{result}"

    end

    def exec_unity(project, command, error_message = nil)
      fail_script_unless_file_exists project
      exec_shell %(#{@bin_unity} -quit -batchmode -projectPath "#{project}" #{command}),
                 error_message.nil? ? "Can't execute unit command: #{command}\nProject: #{project}" : error_message

      unity_log = File.expand_path '~/Library/Logs/Unity/Editor.log'
      fail_script_unless_file_exists unity_log

      result = File.read unity_log
      result =~ /(Exiting batchmode successfully now!)/

      fail_script_unless $1 != nil, "Unity batch failed\n#{result}"
    end

    def import_package(file_package)
      fail_script_unless_file_exists file_package

      exec_unity @dir_project, %(-importPackage "#{file_package}"), "Can't import unity package: #{file_package}"
    end

    def open(error_message = nil)
      exec_shell %(#{@bin_unity} -projectPath "#{@dir_project}"),
                 error_message.nil? ? "Can't open Unity project: #{@dir_project}" : error_message
    end

    def make_custom_args(args)
      if (args != nil && args.length > 0)
        pairs = []
        args.each {|name, value|
          pairs.push %(#{name}=#{value})
        }
        return "-customArgs?#{pairs.join '&'}"
      end
    end

    private :exec_unity, :make_custom_args

  end

end