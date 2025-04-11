"""
Cleanup Manager Utility

This module provides functionality for cleaning up temporary files,
resources, and registry entries created during toolkit execution.
"""
import os
import sys
import shutil
import tempfile
import logging
from typing import List, Dict, Any

class CleanupManager:
    """
    Manages cleanup of temporary files and resources.
    Ensures all temporary artifacts are properly removed on exit.
    """
    
    def __init__(self):
        """Initialize the cleanup manager"""
        self.logger = logging.getLogger("cleanup")
        self.temp_dirs = []
        self.temp_files = []
        self.registry_backups = {}
        self._register_exit_handler()
        
    def _register_exit_handler(self):
        """Register exit handler to ensure cleanup on program exit"""
        import atexit
        atexit.register(self.run)
        
    def add_temp_dir(self, path: str):
        """Add a temporary directory to be cleaned up"""
        if os.path.exists(path) and os.path.isdir(path):
            self.temp_dirs.append(path)
            self.logger.info(f"Registered temp directory for cleanup: {path}")
            
    def add_temp_file(self, path: str):
        """Add a temporary file to be cleaned up"""
        if os.path.exists(path) and os.path.isfile(path):
            self.temp_files.append(path)
            self.logger.info(f"Registered temp file for cleanup: {path}")
            
    def add_registry_backup(self, key_path: str, backup_data: Dict):
        """Add a registry backup for potential restoration"""
        self.registry_backups[key_path] = backup_data
        self.logger.info(f"Registered registry backup for: {key_path}")
        
    def run(self):
        """Run the cleanup process"""
        self.logger.info("Starting cleanup process")
        
        # Clean up temporary files
        for file_path in self.temp_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    self.logger.info(f"Removed temporary file: {file_path}")
            except Exception as e:
                self.logger.error(f"Error removing temporary file {file_path}: {str(e)}")
                
        # Clean up temporary directories
        for dir_path in self.temp_dirs:
            try:
                if os.path.exists(dir_path):
                    shutil.rmtree(dir_path, ignore_errors=True)
                    self.logger.info(f"Removed temporary directory: {dir_path}")
            except Exception as e:
                self.logger.error(f"Error removing temporary directory {dir_path}: {str(e)}")
                
        # Clear lists after cleanup
        self.temp_files = []
        self.temp_dirs = []
        
        self.logger.info("Cleanup process completed")
        
    def restore_registry_backups(self):
        """Restore registry backups if needed"""
        if not self.registry_backups:
            return
            
        self.logger.info("Restoring registry backups")
        
        import winreg
        
        for key_path, backup_data in self.registry_backups.items():
            try:
                key_parts = key_path.split('\\', 1)
                if len(key_parts) != 2:
                    continue
                    
                root_key_str, sub_key = key_parts
                
                # Map string to root key constant
                root_key_map = {
                    "HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
                    "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
                    "HKEY_CLASSES_ROOT": winreg.HKEY_CLASSES_ROOT,
                    "HKEY_USERS": winreg.HKEY_USERS,
                    "HKEY_CURRENT_CONFIG": winreg.HKEY_CURRENT_CONFIG
                }
                
                if root_key_str not in root_key_map:
                    continue
                    
                root_key = root_key_map[root_key_str]
                
                # Open the key
                with winreg.CreateKey(root_key, sub_key) as key:
                    # Restore values
                    for value_name, (value_type, value_data) in backup_data.items():
                        winreg.SetValueEx(key, value_name, 0, value_type, value_data)
                        
                self.logger.info(f"Restored registry backup for: {key_path}")
                
            except Exception as e:
                self.logger.error(f"Error restoring registry backup for {key_path}: {str(e)}")
                
        # Clear backups after restoration
        self.registry_backups = {}