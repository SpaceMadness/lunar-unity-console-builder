import os
import shutil
import subprocess
import time
from pathlib import Path


class Builder:

    # Prints header
    def print_header(self, message):
        print(f"\033[94m{message}\033[0m")

    def print_progress(self, message):
        print(message)

    ############################################################

    # Check condition and raise exception
    def fail_script(self, message):
        raise Exception(f"Build failed! {message}")

    ############################################################

    def fail_script_if(self, condition, message):
        if condition:
            self.fail_script(message)

    ############################################################

    def fail_script_unless(self, condition, message):
        if not condition:
            self.fail_script(message)

    ############################################################

    def fail_script_unless_file_exists(self, path):
        if not path or not (os.path.isdir(path) or os.path.isfile(path)):
            self.fail_script(f"File doesn't exist: '{path}'")

    ############################################################

    def not_nil(self, value):
        self.fail_script_unless(value is not None, 'Value is nil')
        return value

    ############################################################

    def extract_regex(self, text, pattern):
        import re
        match = re.search(pattern, text)
        return match.group(1) if match else None

    ############################################################

    def resolve_path(self, path):
        self.fail_script_unless_file_exists(path)
        return path

    ############################################################

    def build_ios_app(self, proj_dir, proj_name, configuration, target, export_path=None):
        self.fail_script_unless_file_exists(proj_dir)

        os.chdir(proj_dir)
        dir_build = 'build'
        sdk_name = 'iphoneos'

        # Cleanup
        shutil.rmtree(dir_build, ignore_errors=True)

        # Build
        cmd = [
            'xcodebuild',
            f'-project "{proj_name}.xcodeproj"',
            f'-configuration "{configuration}"',
            f'-target "{target}"',
            f'-sdk {sdk_name}'
        ]
        self.exec_shell(" ".join(cmd), "Can't build ios app")

        export_path = export_path or f"build/{configuration}-{sdk_name}"

        os.chdir(export_path)
        app_files = [file for file in os.listdir('.') if file.endswith('.app')]
        self.fail_script_unless(len(app_files) == 1, f"Unexpected apps count: {', '.join(app_files)}")
        return os.path.abspath(app_files[0])

    ############################################################

    def exec_shell(self, command, error_message, options=None):
        if options is None:
            options = {}

        if not options.get('silent', False):
            print(f"Running command: {command}")

        result = subprocess.run(command, shell=True, text=True, capture_output=True)

        if not options.get('dont_fail_on_error', False):
            self.fail_script_unless(result.returncode == 0,
                                    f"{error_message}\nShell failed: {command}\n{result.stderr}")
        else:
            if result.returncode != 0:
                print(error_message)

        return result.stdout

    def delete_file(self, path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        elif os.path.isfile(path):
            os.remove(path)

    def list_files(self, dir, options=None):
        if options is None:
            options = {}

        files = []
        ignored_files = options.get('ignored_files', [])
        types = options.get('types')
        list_directories = options.get('list_directories', False)

        for root, dirs, filenames in os.walk(dir):
            if list_directories:
                for d in dirs:
                    if d not in ignored_files:
                        files.append(os.path.join(root, d))

            for f in filenames:
                if f not in ignored_files and (types is None or os.path.splitext(f)[1] in types):
                    files.append(os.path.join(root, f))

        return files

    def fix_copyrights(self, dir_project, dir_headers, options=None):
        if options is None:
            options = {}

        self.print_header('Fixing copyright...')

        file_header = self.resolve_path(f"{dir_headers}/copyright.txt")
        with open(file_header, 'r') as f:
            copyright_header = f.read()

        files = self.list_files(dir_project, options)
        modified_files = []

        for file in files:
            if self.fix_copyright(file, copyright_header):
                modified_files.append(file)

        return modified_files

    def fix_copyright(self, file, header):
        with open(file, 'r') as f:
            old_source = f.read()

        source_no_header = self.remove_header_comment(old_source)

        header = header.replace("{{date.year}}", str(time.localtime().tm_year))
        header = header.replace("{{file.name.ext}}", os.path.basename(file))
        header = header.replace("{{file.name}}", os.path.splitext(os.path.basename(file))[0])

        new_source = header + '\n\n' + source_no_header

        if new_source != old_source:
            with open(file, 'w') as f:
                f.write(new_source)
            return True

        return False

    def get_release_notes(self, dir_repo, version):
        header = f"## v.{version}"
        file_release_notes = self.resolve_path(f"{dir_repo}/CHANGELOG.md")

        with open(file_release_notes, 'r') as f:
            lines = f.readlines()

        start_index = next((i for i, line in enumerate(lines) if header in line), -1)
        end_index = next(
            (i for i, line in enumerate(lines[start_index + 1:], start=start_index + 1) if "## v." in line), len(lines))

        self.fail_script_unless(start_index != -1 and end_index != -1, "Can't extract release notes")

        notes = ''.join(lines[start_index + 1:end_index]).strip()
        notes = notes.replace('"', '\\"').replace('``', '\\`')
        return notes

    @staticmethod
    def remove_header_comment(source):
        # Placeholder for actual implementation
        return source
