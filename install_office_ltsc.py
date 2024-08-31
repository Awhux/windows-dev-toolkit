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
import uuid
import logging
from rich.console import Console
from rich.prompt import Prompt
from rich.logging import RichHandler

console = Console()
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
log = logging.getLogger("rich")

office_deployment_tool_link = "https://download.microsoft.com/download/2/7/A/27AF1BE6-DD20-4CB4-B154-EBAB8A7D4A7E/officedeploymenttool_17830-20162.exe"
configuration_x64 = "https://gist.githubusercontent.com/Awhux/517b3ce82116cd170c8a31c95fbbcb3f/raw/74804495f48d4d80dd0ee76ecebbb3d2cd76caea/config_x64.xml"
configuration_x86 = "https://gist.githubusercontent.com/Awhux/517b3ce82116cd170c8a31c95fbbcb3f/raw/74804495f48d4d80dd0ee76ecebbb3d2cd76caea/config_x86.xml"

def download_file(url, filename):
    response = requests.get(url)
    with open(filename, 'wb') as file:
        file.write(response.content)

def create_temp_dir():
    temp_base = tempfile.gettempdir()
    unique_dir = f"office_install_{uuid.uuid4().hex}"
    path = os.path.join(temp_base, unique_dir)
    os.makedirs(path, exist_ok=True)
    return path

def clean_up(path):
    try:
        shutil.rmtree(path)
        log.info(f"Cleaned up temporary directory: {path}")
    except Exception as e:
        log.warning(f"Could not remove temporary directory {path}. Error: {e}")
        log.warning("You may want to manually delete this directory later.")

def validate_config(config_file):
    with open(config_file, 'r') as file:
        content = file.read()
    if "<Configuration>" in content and "</Configuration>" in content:
        log.info(f"Configuration file {config_file} appears to be valid.")
        return True
    else:
        log.error(f"Configuration file {config_file} appears to be invalid.")
        return False

def main():
    log.info("Installing Office products")

    temp_dir = create_temp_dir()
    log.info(f"Created temporary directory: {temp_dir}")

    try:
        os.chdir(temp_dir)

        log.info("Downloading Office Deployment Tool...")
        download_file(office_deployment_tool_link, "officedeploymenttool.exe")

        log.info("Extracting Office Deployment Tool...")
        subprocess.run(["officedeploymenttool.exe", "/quiet", "/extract:."], check=True)

        log.info("Downloading configuration files...")
        download_file(configuration_x64, "config_x64.xml")
        download_file(configuration_x86, "config_x86.xml")

        architecture = platform.architecture()[0]
        config_file = "config_x64.xml" if architecture == "64bit" else "config_x86.xml"

        if not validate_config(config_file):
            raise ValueError(f"Invalid configuration file: {config_file}")

        log.info(f"Running Office Deployment Tool with {config_file}...")
        result = subprocess.run(["setup.exe", "/configure", config_file], capture_output=True, text=True)
        
        if result.returncode != 0:
            log.error(f"Office Deployment Tool failed with exit code {result.returncode}")
            log.error(f"stdout: {result.stdout}")
            log.error(f"stderr: {result.stderr}")
            raise subprocess.CalledProcessError(result.returncode, result.args, result.stdout, result.stderr)

        log.info("Office installation complete!")

    except Exception as e:
        log.exception("An error occurred during the installation process")
    finally:
        clean_up(temp_dir)

    if Prompt.ask("Do you want to reboot the system now?", choices=["y", "n"]) == "y":
        log.info("Rebooting system...")
        if sys.platform == "win32":
            os.system("shutdown /r /t 0")
        else:
            os.system("reboot")
    else:
        log.info("Please remember to reboot your system to complete the installation.")

if __name__ == "__main__":
    main()