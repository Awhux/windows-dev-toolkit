"""
Office LTSC Management Module

This module handles legitimate Office LTSC deployment scenarios for
enterprise environments using volume licensing.
"""
import os
import subprocess
import tempfile
import logging
import requests
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, Optional

class OfficeLTSCManager:
    """
    Manages Office LTSC deployment using the Office Deployment Tool (ODT)
    for legitimate enterprise deployment scenarios.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("office_ltsc")
        self.temp_dir = None
        self.odt_path = None
    
    def execute(self, ui):
        """Main execution flow for Office LTSC management"""
        options = [
            "Download Office Deployment Tool",
            "Configure Office LTSC deployment",
            "Deploy Office LTSC (requires volume license)",
            "Remove Office installations",
            "Back to main menu"
        ]
        
        while True:
            choice = ui.display_menu("Office LTSC Management", options)
            
            if choice == 4:  # Back to main menu
                break
            elif choice == 0:
                self._download_odt(ui)
            elif choice == 1:
                self._configure_deployment(ui)
            elif choice == 2:
                self._deploy_office(ui)
            elif choice == 3:
                self._remove_office(ui)
    
    def _download_odt(self, ui):
        """Download the official Office Deployment Tool"""
        ui.display_info("Downloading Office Deployment Tool...")
        
        try:
            # Create temporary directory
            self.temp_dir = tempfile.mkdtemp()
            self.logger.info(f"Created temporary directory: {self.temp_dir}")
            
            # Download ODT from official Microsoft source
            odt_url = "https://download.microsoft.com/download/2/7/A/27AF1BE6-DD20-4CB4-B154-EBAB8A7D4A7E/officedeploymenttool_16327-20214.exe"
            odt_installer = os.path.join(self.temp_dir, "odt_installer.exe")
            
            ui.display_progress("Downloading Office Deployment Tool...")
            response = requests.get(odt_url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            
            with open(odt_installer, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        ui.update_progress(downloaded / total_size * 100)
            
            # Extract ODT
            ui.display_info("Extracting Office Deployment Tool...")
            self.odt_path = os.path.join(self.temp_dir, "ODT")
            os.makedirs(self.odt_path, exist_ok=True)
            
            # Run the ODT installer to extract
            result = subprocess.run(
                [odt_installer, "/extract:", self.odt_path, "/quiet"],
                check=True
            )
            
            if result.returncode == 0:
                ui.display_success("Office Deployment Tool downloaded successfully")
                self.logger.info(f"ODT extracted to {self.odt_path}")
            else:
                ui.display_error("Failed to extract Office Deployment Tool")
                
        except Exception as e:
            ui.display_error(f"Error downloading ODT: {str(e)}")
            self.logger.error(f"ODT download error: {str(e)}")
    
    def _configure_deployment(self, ui):
        """Configure Office LTSC deployment XML"""
        if not self._check_odt(ui):
            return
            
        ui.display_info("Configuring Office LTSC deployment...")
        
        # Get user configuration choices
        config = {}
        config["architecture"] = ui.prompt_choice("Select architecture:", ["32-bit", "64-bit"])
        config["language"] = ui.prompt_input("Enter language (e.g., en-us):", default="en-us")
        
        # Product selection
        products = [
            "Office LTSC Professional Plus 2021 - Volume License",
            "Office LTSC Standard 2021 - Volume License",
            "Visio LTSC Professional 2021 - Volume License",
            "Project LTSC Professional 2021 - Volume License"
        ]
        
        config["products"] = ui.prompt_multichoice("Select products to install:", products)
        
        # Generate configuration XML
        xml_content = self._generate_config_xml(config)
        config_path = os.path.join(self.odt_path, "configuration.xml")
        
        try:
            with open(config_path, "w") as f:
                f.write(xml_content)
            
            ui.display_success("Configuration file created successfully")
            ui.display_info(f"Configuration saved to: {config_path}")
            
        except Exception as e:
            ui.display_error(f"Error creating configuration: {str(e)}")
            self.logger.error(f"Configuration error: {str(e)}")
    
    def _generate_config_xml(self, config):
        """Generate Office LTSC configuration XML"""
        # Map user-friendly names to product IDs
        product_map = {
            "Office LTSC Professional Plus 2021 - Volume License": "ProPlus2021Volume",
            "Office LTSC Standard 2021 - Volume License": "Standard2021Volume",
            "Visio LTSC Professional 2021 - Volume License": "VisioPro2021Volume",
            "Project LTSC Professional 2021 - Volume License": "ProjectPro2021Volume"
        }
        
        # Create XML structure
        root = ET.Element("Configuration")
        
        # Add channel
        add = ET.SubElement(root, "Add", {
            "OfficeClientEdition": "32" if config["architecture"] == 0 else "64",
            "Channel": "PerpetualVL2021"
        })
        
        # Add selected products
        for product_idx in config["products"]:
            product_id = product_map[list(product_map.keys())[product_idx]]
            product = ET.SubElement(add, "Product", {"ID": product_id})
            ET.SubElement(product, "Language", {"ID": config["language"]})
        
        # Add display settings
        display = ET.SubElement(root, "Display", {
            "Level": "Full",
            "AcceptEULA": "TRUE"
        })
        
        # Add property settings
        property_elem = ET.SubElement(root, "Property", {"Name": "AUTOACTIVATE", "Value": "0"})
        
        # Convert to string
        xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml_str += ET.tostring(root, encoding="unicode")
        
        return xml_str
    
    def _deploy_office(self, ui):
        """Deploy Office LTSC using configuration"""
        if not self._check_odt(ui):
            return
            
        # Check if configuration exists
        config_path = os.path.join(self.odt_path, "configuration.xml")
        if not os.path.exists(config_path):
            ui.display_error("Configuration file not found. Please configure deployment first.")
            return
        
        # Confirm with user
        if not ui.confirm("WARNING: This will install Office LTSC using your volume license. Continue?"):
            ui.display_info("Deployment cancelled")
            return
        
        ui.display_warning(
            "IMPORTANT: This tool assumes you have a valid volume license for the products being installed. "
            "Using this tool without proper licensing is a violation of Microsoft's terms of service."
        )
        
        if not ui.confirm("I confirm that I have proper licensing for this deployment"):
            ui.display_info("Deployment cancelled")
            return
        
        # Run deployment
        try:
            ui.display_info("Starting Office LTSC deployment...")
            setup_path = os.path.join(self.odt_path, "setup.exe")
            
            result = subprocess.run(
                [setup_path, "/configure", config_path],
                check=True
            )
            
            if result.returncode == 0:
                ui.display_success("Office LTSC deployment completed successfully")
            else:
                ui.display_error("Office LTSC deployment failed")
                
        except Exception as e:
            ui.display_error(f"Deployment error: {str(e)}")
            self.logger.error(f"Deployment error: {str(e)}")
    
    def _remove_office(self, ui):
        """Remove Office installations"""
        if not self._check_odt(ui):
            return
            
        # Confirm with user
        if not ui.confirm("WARNING: This will remove Office installations. Continue?"):
            ui.display_info("Removal cancelled")
            return
        
        # Create removal configuration
        remove_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Configuration>
  <Remove All="TRUE" />
  <Display Level="Full" AcceptEULA="TRUE" />
</Configuration>
"""
        
        remove_path = os.path.join(self.odt_path, "remove_config.xml")
        
        try:
            with open(remove_path, "w") as f:
                f.write(remove_xml)
            
            # Run removal
            ui.display_info("Removing Office installations...")
            setup_path = os.path.join(self.odt_path, "setup.exe")
            
            result = subprocess.run(
                [setup_path, "/configure", remove_path],
                check=True
            )
            
            if result.returncode == 0:
                ui.display_success("Office removal completed successfully")
            else:
                ui.display_error("Office removal failed")
                
        except Exception as e:
            ui.display_error(f"Removal error: {str(e)}")
            self.logger.error(f"Removal error: {str(e)}")
    
    def _check_odt(self, ui):
        """Check if ODT is downloaded and available"""
        if not self.odt_path or not os.path.exists(self.odt_path):
            ui.display_error("Office Deployment Tool not found. Please download it first.")
            return False
        return True
        
    def cleanup(self):
        """Clean up temporary files"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            import shutil
            try:
                shutil.rmtree(self.temp_dir)
                self.logger.info(f"Removed temporary directory: {self.temp_dir}")
            except Exception as e:
                self.logger.error(f"Error cleaning up: {str(e)}")