# Use Windows Server Core as base image
FROM mcr.microsoft.com/windows/servercore:ltsc2022

# Set shell to PowerShell
SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop'; $ProgressPreference = 'SilentlyContinue';"]

# Set working directory
WORKDIR C:/App

# Install Chocolatey
RUN Set-ExecutionPolicy Bypass -Scope Process -Force; \
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; \
    iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

# Install Python
RUN choco install python -y --version=3.10.0

# Refresh environment variables
RUN refreshenv

# Install PyInstaller and other dependencies
RUN python -m pip install --upgrade pip && \
    python -m pip install pyinstaller pytest pytest-cov black flake8 pywin32 requests psutil colorama prompt_toolkit tqdm

# Copy project files
COPY . .

# Build the executable
RUN python -m PyInstaller --onefile --clean --add-data "windows_dev_toolkit/resources/*;windows_dev_toolkit/resources/" \
    --name WinDevToolkit.exe --uac-admin --hidden-import win32api --hidden-import win32con \
    --hidden-import winreg --hidden-import psutil \
    windows_dev_toolkit/main.py

# Output folder that contains the final built executable
VOLUME C:/App/dist

# Default command when container starts
CMD ["powershell"]