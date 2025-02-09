import os
import subprocess


class UnityProject:
    def __init__(self, dir_project, bin_unity):
        self.dir_project = os.path.abspath(dir_project)
        self.bin_unity = os.path.abspath(bin_unity)

    def exec_unity_method(self, method, args=None, error_message=None):
        self.exec_unity_method_opt(
            self.dir_project, method, args or {}, {}, error_message
        )

    def exec_unity_method_opt(
            self, project, method, args=None, options=None, error_message=None
    ):
        if args is None:
            args = {}
        if options is None:
            options = {}

        cmd = [f'"{self.bin_unity}"']
        if "no_quit" not in options:
            cmd.append("-quit")
        if "no_batch" not in options:
            cmd.append("-batchmode")
        if args:
            cmd.append(f'"{self.make_custom_args(args)}"')
        cmd.append(f"-executeMethod {method}")
        cmd.append(f'-projectPath "{project}"')

        cmd_str = " ".join(cmd)
        self.exec_shell(
            cmd_str,
            error_message
            or f"Can't execute method: {method}\nProject: {project}",
        )

        unity_log = os.path.expand_path(Builder.BuildPlatform.unity_log_path())
        self.fail_script_unless_file_exists(unity_log)

        with open(unity_log, "r") as f:
            result = f.read()

        if "Exiting batchmode successfully now!" not in result:
            self.fail_script_unless(
                False, f"Unity batch failed\n{result}"
            )

    def exec_unity(self, project, command, error_message=None):
        self.fail_script_unless_file_exists(project)

        cmd = (
            f'{self.bin_unity} -quit -batchmode -projectPath "{project}" {command}'
        )
        self.exec_shell(
            cmd,
            error_message
            or f"Can't execute unit command: {command}\nProject: {project}",
        )

        unity_log = os.path.expanduser("~/Library/Logs/Unity/Editor.log")
        self.fail_script_unless_file_exists(unity_log)

        with open(unity_log, "r") as f:
            result = f.read()

        if "Exiting batchmode successfully now!" not in result:
            self.fail_script_unless(
                False, f"Unity batch failed\n{result}"
            )

    def import_package(self, file_package):
        self.fail_script_unless_file_exists(file_package)

        self.exec_unity(
            self.dir_project,
            f'-importPackage "{file_package}"',
            f"Can't import unity package: {file_package}",
        )

    def open(self, error_message=None):
        cmd = f'{self.bin_unity} -projectPath "{self.dir_project}"'
        self.exec_shell(
            cmd,
            error_message or f"Can't open Unity project: {self.dir_project}",
        )

    def make_custom_args(self, args):
        if args:
            pairs = [f"{name}={value}" for name, value in args.items()]
            return f"-customArgs?{'&'.join(pairs)}"
        return ""

    @staticmethod
    def exec_shell(cmd, error_message):
        try:
            subprocess.run(cmd, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(error_message) from e

    @staticmethod
    def fail_script_unless(condition, message):
        if not condition:
            raise RuntimeError(message)

    @staticmethod
    def fail_script_unless_file_exists(file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")


# Replace Builder::Platform.unity_log in Ruby with an equivalent function or path in Python
class Platform:
    @staticmethod
    def unity_log():
        return "~/Library/Logs/Unity/Editor.log"
