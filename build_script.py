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
        '--add-data', f'main.py:.',  # Include main.py as data
    ]
    
    # Add all Python files as data files
    for file in python_files:
        command.extend(['--add-data', f'{file}:.'])
    
    # Add hidden imports
    command.extend([
        '--hidden-import=typer',
        '--hidden-import=rich',
        '--hidden-import=yaspin',
        '--hidden-import=click',
        'main.py'
    ])
    
    # Run the PyInstaller command
    subprocess.run(command, check=True)

if __name__ == '__main__':
    build_executable()