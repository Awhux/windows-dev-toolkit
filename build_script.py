import os
import glob
import subprocess
import sys

def build_executable():
    # Get all Python files except main.py and build_script.py
    python_files = glob.glob('*.py')
    python_files = [f for f in python_files if f not in ['main.py', 'build_script.py']]

    # Prepare the PyInstaller command
    command = [
        sys.executable,  # Use the current Python interpreter
        '-m', 'PyInstaller',
        '--onefile',
        '--name=script_runner',
        '--add-data', f'main.py{os.pathsep}.',  # Include main.py as data
    ]

    # Add all Python files as data files
    for file in python_files:
        command.extend(['--add-data', f'{file}{os.pathsep}.'])

    # Add hidden imports
    hidden_imports = [
        'typer',
        'rich',
        'yaspin',
        'click',
        'ipaddress',
        'pathlib',
        'urllib.parse',
    ]
    for imp in hidden_imports:
        command.extend(['--hidden-import', imp])

    # Add PyInstaller options to help with module importing
    command.extend([
        '--collect-all', 'typer',
        '--collect-all', 'rich',
        '--collect-all', 'yaspin',
        '--collect-all', 'click',
        '--collect-all', 'requests',
    ])

    # Add main script
    command.append('main.py')

    print("Running PyInstaller with command:", ' '.join(command))

    # Run the PyInstaller command
    subprocess.run(command, check=True)

if __name__ == '__main__':
    build_executable()