import os
import shutil
import subprocess
import time
from pathlib import Path

import re
from typing import Optional


# Prints header
def print_header(message):
    print(f"\033[94m{message}\033[0m")


def print_progress(message):
    print(message)


############################################################

# Check condition and raise exception
def fail_script(message):
    raise Exception(f"Build failed! {message}")


############################################################

def fail_script_if(condition, message):
    if condition:
        fail_script(message)


############################################################

def fail_script_unless(condition, message):
    if not condition:
        fail_script(message)


############################################################

def fail_script_unless_file_exists(path: str):
    if not path or not Path(path).exists():
        fail_script(f"File doesn't exist: '{path}'")


############################################################

def not_nil(value):
    fail_script_unless(value is not None, 'Value is nil')
    return value


############################################################

def read_text(file_path: str) -> str:
    """Reads the content of a file and returns it as a string."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def write_text(file_path: str, content: str) -> None:
    """Writes the given content string to a file."""
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)


def find_in_text(text: str, pattern: str) -> Optional[str]:
    """Searches for the first occurrence of a regex pattern in the given text and returns the matching group."""
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    return None


def find_in_file(file_path: str, pattern: str) -> Optional[str]:
    """Reads a file and searches for the first occurrence of a regex pattern, returning the matching group."""
    text = read_text(file_path)
    return find_in_text(text, pattern)


def extract_regex(text, pattern) -> str:
    import re
    match = re.search(pattern, text)
    return match.group(1) if match else None


def join_path(*components) -> str:
    """
    Joins multiple path components together in a platform-independent way.
    """
    return os.path.join(*components)


############################################################

def resolve_path(path: str):
    fail_script_unless_file_exists(path)
    return path


############################################################

def build_ios_app(proj_dir, proj_name, configuration, target, export_path=None):
    fail_script_unless_file_exists(proj_dir)

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
    exec_shell(" ".join(cmd), "Can't build ios app")

    export_path = export_path or f"build/{configuration}-{sdk_name}"

    os.chdir(export_path)
    app_files = [file for file in os.listdir('.') if file.endswith('.app')]
    fail_script_unless(len(app_files) == 1, f"Unexpected apps count: {', '.join(app_files)}")
    return os.path.abspath(app_files[0])


############################################################

def exec_shell(command, error_message=None, **kwargs) -> str:
    """
    Execute a shell command and handle the result.

    Args:
        command: The shell command to execute
        error_message: Error message to display if command fails
        **kwargs: Additional arguments:
            silent (bool): If True, suppress command output
            dont_fail_on_error (bool): If True, don't raise error on non-zero exit code

    Returns:
        str: Command stdout output

    Raises:
        RuntimeError: If command fails and dont_fail_on_error is False
    """
    if not kwargs.get('silent', False):
        print(f"Running command: {command}")

    result = subprocess.run(command,
                            shell=True,
                            text=True,
                            capture_output=True,
                            cwd=kwargs.get("working_dir"))

    if result.returncode != 0:
        error = f"{error_message}\nShell failed: {command}\n{result.stderr}"
        if not kwargs.get('dont_fail_on_error', False):
            fail_script_unless(False, error)
        else:
            print(error)

    return result.stdout


def delete_file(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.isfile(path):
        os.remove(path)


def list_files(path, types, ignored_files, list_directories=False):
    files = []
    for root, dirs, filenames in os.walk(path):
        if list_directories:
            for d in dirs:
                if d not in ignored_files:
                    files.append(os.path.join(root, d))

        for f in filenames:
            if f not in ignored_files and (types is None or os.path.splitext(f)[1] in types):
                files.append(os.path.join(root, f))

    return files


def fix_copyrights(dir_project, dir_headers, **kwargs) -> list[str]:
    print_header('Fixing copyright...')

    file_header = resolve_path(f"{dir_headers}/copyright.txt")
    copyright_header = read_text(file_header)

    files = list_files(dir_project,
                       types=kwargs.get('types'),
                       ignored_files=kwargs.get('ignored_files', []),
                       list_directories=kwargs.get('list_directories', False))

    return [file for file in files if _fix_copyright(file, copyright_header)]


def _fix_copyright(file, header):
    """Updates copyright header in a file if needed.
    
    Args:
        file: Path to the source file
        header: Copyright header template string
    
    Returns:
        bool: True if file was modified, False otherwise
    """
    old_source = read_text(file)
    source_no_header = remove_header_comment(old_source)

    # Get file info
    filename = os.path.basename(file)
    name, _ = os.path.splitext(filename)
    current_year = str(time.localtime().tm_year)

    # Format header template
    header = header.replace("{{date.year}}", current_year)
    header = header.replace("{{file.name.ext}}", filename)
    header = header.replace("{{file.name}}", name)

    new_source = f"{header}\n\n{source_no_header}"

    if new_source == old_source:
        return False

    write_text(file, new_source)
    return True


def get_release_notes(dir_repo, version):
    header = f"## v.{version}"
    file_release_notes = resolve_path(f"{dir_repo}/CHANGELOG.md")

    with open(file_release_notes, 'r') as f:
        lines = f.readlines()

    start_index = next((i for i, line in enumerate(lines) if header in line), -1)
    end_index = next(
        (i for i, line in enumerate(lines[start_index + 1:], start=start_index + 1) if "## v." in line), len(lines))

    fail_script_unless(start_index != -1 and end_index != -1, "Can't extract release notes")

    notes = ''.join(lines[start_index + 1:end_index]).strip()
    notes = notes.replace('"', '\\"').replace('``', '\\`')
    return notes


def remove_header_comment(source: str) -> str:
    """Removes header comments from source code.
    
    Handles different comment styles:
    - // Single line comments (C-style)
    - # Single line comments (Python/Shell-style)
    - /* */ Multi-line comments (C-style)
    - ''' ''' Multi-line comments (Python-style)
    - \"\"\" \"\"\" Multi-line comments (Python-style)
    
    Args:
        source: Source code as string
        
    Returns:
        Source code with header comments removed
    """
    # Skip leading whitespace
    source = source.lstrip()
    
    # Handle empty source
    if not source:
        return source
        
    # Handle single-line comments
    lines = source.splitlines()
    first_non_comment = 0
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        if not stripped:
            continue
        if not stripped.startswith(('//', '#', '/*', '<!--')):
            first_non_comment = i
            break
    
    # Handle multi-line comments
    if first_non_comment == 0:
        # C-style /* */ comments
        if source.lstrip().startswith('/*'):
            end = source.find('*/') 
            if end != -1:
                return source[end + 2:].lstrip()
                
        # Python-style triple quotes
        for delimiter in ['"""', "'''"]:
            if source.lstrip().startswith(delimiter):
                end = source.find(delimiter, len(delimiter))
                if end != -1:
                    return source[end + 3:].lstrip()
    
    return '\n'.join(lines[first_non_comment:])
