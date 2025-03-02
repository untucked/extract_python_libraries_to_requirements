import os
import ast
import tkinter as tk
from tkinter import filedialog
# List of pre-loaded Python libraries to skip
PRE_LOADED_LIBRARIES = {
    'abc', 'aifc', 'antigravity', 'argparse', 'array', 'ast', 'asynchat', 'asyncio', 'atlas',
    'bdb', 'binascii', 'binhex', 'builtins', 'cProfile', 'calendar', 'code', 'codeop', 'collections',
    'colorsys', 'compile', 'concurrent', 'configparser', 'contextlib', 'copy', 'crypt', 'ctypes',
    'datetime', 'decimal', 'difflib', 'dis', 'distutils', 'dumb', 'email', 'encodings', 'functools',
    'genericpath', 'getopt', 'getpass', 'gettext', 'glob', 'gc', 'grp', 'hashlib', 'heapq', 'itertools',
    'json', 'keyword', 'lib2to3', 'locale', 'logging', 'lzma', 'macpath', 'math', 'msilib', 'multiprocessing',
    'multithreading', 'numbers', 'operator', 'optparse', 'os', 'pdb', 'pickle', 'pip', 'pkgutil', 'platform',
    'plistlib', 'poplib', 'posix', 'pprint', 'profile', 'pstats', 'pwd', 'queue', 'random', 're',
    'repr', 'resource', 'rlock', 'runpy', 'smtpd', 'smtplib', 'socket', 'sqlite3', 'stat', 'statistics',
    'string', 'struct', 'subprocess', 'symbol', 'symtable', 'sys', 'sysconfig', 'tabnanny', 'tarfile',
    'telnetlib', 'tempfile', 'textwrap', 'threading', 'time', 'token', 'tokenize', 'trace', 'traceback',
    'types', 'typing', 'unicodedata', 'unittest', 'urllib', 'uuid', 'warnings', 'wave', 'weakref',
    'webbrowser', 'windows', 'wsgiref', 'zipapp', 'zipfile', 'zlib'
}

def get_local_modules(directory):
    # Look for directories or .py files (excluding __init__.py) that could be local modules
    local_modules = set()
    for item in os.listdir(directory):
        path = os.path.join(directory, item)
        if os.path.isdir(path) and not item.startswith('__'):
            local_modules.add(item)
        elif os.path.isfile(path) and item.endswith('.py'):
            module_name = os.path.splitext(item)[0]
            local_modules.add(module_name)
    return local_modules

def get_python_files(directory):
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files

def extract_imports(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        file_content = file.read()

    tree = ast.parse(file_content)
    imports = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                # Only take the top-level module
                top_module = alias.name.split('.')[0]
                imports.add(top_module)
        elif isinstance(node, ast.ImportFrom):
            # Only add if it's not a relative import (node.level == 0)
            if node.module and node.level == 0:
                top_module = node.module.split('.')[0]
                imports.add(top_module)

    return imports


def select_directory():
    def select_directory_box():
        # Open the file dialog to select a directory
        directory = filedialog.askdirectory()
        return directory

    # Create the main window
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Call the function to select the directory
    return select_directory_box()


def main(directory_to_search=None):
    if not directory_to_search:
        directory_to_search = select_directory()
    if not os.path.isdir(directory_to_search):
        print("The specified directory does not exist. Please try again.")
        return

    python_files = get_python_files(directory_to_search)
    all_imports = set()

    for file in python_files:
        imports = extract_imports(file)
        all_imports.update(imports)

    local_modules = get_local_modules(directory_to_search)

    # Filter out pre-loaded libraries and local modules
    unique_imports = {
        imp for imp in all_imports 
        if imp not in PRE_LOADED_LIBRARIES and imp not in local_modules
    }

    # Check if requirements.txt exists in the directory
    requirements_file_path = os.path.join(directory_to_search, 'requirements.txt')
    if 'requirements.txt' not in os.listdir(directory_to_search):
        with open(requirements_file_path, 'w', encoding='utf-8') as req_file:
            for library in sorted(unique_imports):
                req_file.write(f"{library}\n")
        print(f"Requirements file 'requirements.txt' generated successfully.")
    else:
        print("Requirements file 'requirements.txt' already exists in the directory.")
        with open(os.path.join(directory_to_search, 'requirements_generated.txt'), 'w', encoding='utf-8') as req_file:
            for library in sorted(unique_imports):
                req_file.write(f"{library}\n")
        print(f"Requirements file 'requirements_generated.txt' generated successfully with {len(unique_imports)} unique libraries.")

if __name__ == "__main__":
    # directory_to_search = r'C:\Users\bradley.eylander\OneDrive - LMI Consulting\Documents\Python\rfid_tracer'
    # directory_to_search = '.'
    directory_to_search=None
    main(directory_to_search=directory_to_search)
