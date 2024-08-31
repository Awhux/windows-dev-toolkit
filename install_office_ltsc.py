"""
Install and activate WPS Office LTSC
"""
import os
import sys
import subprocess
import requests
import platform
import tempfile
import shutil
from rich.console import Console
from rich.prompt import Prompt

console = Console()

office_deployment_tool_link = "https://download.microsoft.com/download/2/7/A/27AF1BE6-DD20-4CB4-B154-EBAB8A7D4A7E/officedeploymenttool_17830-20162.exe"
configuration_x64 = "https://gist.githubusercontent.com/Awhux/517b3ce82116cd170c8a31c95fbbcb3f/raw/74804495f48d4d80dd0ee76ecebbb3d2cd76caea/config_x64.xml"
configuration_x86 = "https://gist.githubusercontent.com/Awhux/517b3ce82116cd170c8a31c95fbbcb3f/raw/74804495f48d4d80dd0ee76ecebbb3d2cd76caea/config_x86.xml"

def download_file(url, filename):
    response = requests.get(url)
    with open(filename, 'wb') as file:
        file.write(response.content)

def main():
    console.print("[bold blue]Installing Office products[/bold blue]")

    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        console.print(f"Created temporary directory: {temp_dir}")

        # Change to the temporary directory
        os.chdir(temp_dir)

        # Download Office Deployment Tool
        console.print("Downloading Office Deployment Tool...")
        download_file(office_deployment_tool_link, "officedeploymenttool.exe")

        # Extract the Office Deployment Tool
        console.print("Extracting Office Deployment Tool...")
        subprocess.run(["officedeploymenttool.exe", "/quiet", "/extract:."], check=True)

        # Download the configurations for x64 and x86
        console.print("Downloading configuration files...")
        download_file(configuration_x64, "config_x64.xml")
        download_file(configuration_x86, "config_x86.xml")

        # Get the system architecture
        architecture = platform.architecture()[0]

        # Run the office deployment tool with the correct configuration
        if architecture == "64bit":
            config_file = "config_x64.xml"
        else:
            config_file = "config_x86.xml"

        console.print(f"Running Office Deployment Tool with {config_file}...")
        subprocess.run(["setup.exe", "/configure", config_file], check=True)

        console.print("[bold green]Office installation complete![/bold green]")

    # Prompt for system reboot
    if Prompt.ask("Do you want to reboot the system now?", choices=["y", "n"]) == "y":
        console.print("Rebooting system...")
        if sys.platform == "win32":
            os.system("shutdown /r /t 0")
        else:
            os.system("reboot")
    else:
        console.print("Please remember to reboot your system to complete the installation.")

if __name__ == "__main__":
    main()