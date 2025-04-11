"""
Windows Developer Utilities Toolkit

Main entry point for the toolkit application.
"""
import argparse
import logging
import os
import sys
from pathlib import Path

# Local modules
from src.utils.admin_check import verify_admin_privileges
from src.utils.cleanup import CleanupManager
from src.utils.ui import TUIManager
from src.utils.feature_detection import FeatureDetection
from src.modules.environment_setup import EnvironmentManager
from src.modules.office_deployment import OfficeLTSCManager
from src.modules.windows_config import WindowsConfigManager
from src.modules.developer_keys import DeveloperKeyManager

class DeveloperToolkit:
    """Main toolkit controller for Windows Developer Utilities"""
    
    def __init__(self):
        """Initialize the toolkit"""
        self.logger = self._setup_logging()
        self.config = self._load_config()
        self.tui = TUIManager()
        self.cleanup = CleanupManager()
        self.feature_detection = FeatureDetection()
        
        # Register modules
        self.modules = {
            "environment": EnvironmentManager(self.config),
            "office": OfficeLTSCManager(self.config),
            "windows": WindowsConfigManager(self.config),
            "devkeys": DeveloperKeyManager(self.config)
        }
    
    def _setup_logging(self):
        """Configure logging"""
        log_dir = Path.home() / ".windows_dev_toolkit" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / "toolkit.log"
        
        # Configure root logger
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        
        # Configure file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_format = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_format)
        
        # Add handlers
        logger.addHandler(file_handler)
        
        return logger
        
    def _load_config(self):
        """Load configuration"""
        # For now, return a simple default config
        # In a real implementation, this would load from a file
        return {
            "environment": {
                "python": {
                    "packages": ["pytest", "black", "flake8", "pytest-cov"]
                },
                "node": {
                    "packages": ["typescript", "eslint", "prettier"]
                }
            },
            "windows": {
                "features": ["Microsoft-Windows-Subsystem-Linux", "NetFx3"]
            },
            "office": {
                "products": ["ProPlus2021Volume", "VisioPro2021Volume"]
            }
        }
    
    def run(self):
        """Main execution flow"""
        if not verify_admin_privileges():
            self.tui.display_error("Administrator privileges required")
            sys.exit(1)
            
        try:
            # Display welcome screen
            self.tui.display_welcome()
            
            # Detect system features
            self.tui.display_info("Detecting system features...")
            features = self.feature_detection.get_all_features()
            
            # Main menu loop
            while True:
                choice = self.tui.display_main_menu()
                if choice == "exit":
                    break
                elif choice in self.modules:
                    self.modules[choice].execute(self.tui)
                    
        except Exception as e:
            self.logger.error(f"Critical error: {str(e)}")
            self.tui.display_error(f"An error occurred: {str(e)}")
        finally:
            # Run cleanup
            self.cleanup.run()
            self.tui.display_goodbye()

def main():
    """Entry point function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Windows Developer Utilities Toolkit")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--version", action="store_true", help="Show version and exit")
    
    args = parser.parse_args()
    
    if args.version:
        print("Windows Developer Utilities Toolkit v1.0.0")
        return
    
    # Run the toolkit
    toolkit = DeveloperToolkit()
    toolkit.run()

if __name__ == "__main__":
    main()