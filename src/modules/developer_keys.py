"""
Developer Key Management Module

This module handles Windows developer key registration, validation, and secure storage.
"""
import os
import logging
import base64
import json
import re
import hashlib
import secrets
import winreg
from typing import Dict, Any, Optional, Tuple, List
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class DeveloperKeyManager:
    """
    Manages Windows developer keys for legitimate development environments.
    Provides functionality for key registration, validation, and secure storage.
    """
    
    # Registry paths
    REG_KEY_PATH = r"SOFTWARE\YourCompany\DeveloperToolkit"
    REG_KEY_SALT_VALUE = "KeyStoreSalt"
    REG_KEY_STORE_VALUE = "SecureKeyStore"
    
    # Key validation patterns
    KEY_PATTERNS = {
        "windows_dev": re.compile(r'^[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}$'),
        "enterprise": re.compile(r'^ENTDEV-[A-Z0-9]{16}-[A-Z0-9]{8}$'),
        "visual_studio": re.compile(r'^VS-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$')
    }
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the developer key manager"""
        self.config = config
        self.logger = logging.getLogger("dev_keys")
        self.machine_id = self._get_machine_id()
    
    def execute(self, ui):
        """Main execution flow for developer key management"""
        options = [
            "Register new developer key",
            "View registered keys",
            "Validate developer key",
            "Remove developer key",
            "Back to main menu"
        ]
        
        while True:
            choice = ui.display_menu("Developer Key Management", options)
            
            if choice == 4:  # Back to main menu
                break
            elif choice == 0:
                self._register_key(ui)
            elif choice == 1:
                self._view_keys(ui)
            elif choice == 2:
                self._validate_key(ui)
            elif choice == 3:
                self._remove_key(ui)
    
    def _register_key(self, ui):
        """Register a new developer key"""
        ui.display_info("Registering a new developer key...")
        
        # Get key information
        key_type_options = ["Windows Developer Key", "Enterprise Developer Key", "Visual Studio Key"]
        key_type_idx = ui.prompt_choice("Select key type:", key_type_options)
        key_type = ["windows_dev", "enterprise", "visual_studio"][key_type_idx]
        
        # Get key value
        while True:
            key_value = ui.prompt_input(f"Enter {key_type_options[key_type_idx]} value:")
            
            # Validate key format
            if not self._validate_key_format(key_type, key_value):
                ui.display_error(f"Invalid key format. Please check and try again.")
                if not ui.confirm("Try again?"):
                    return
                continue
            
            # Check if key already exists
            if self._key_exists(key_value):
                ui.display_error("This key is already registered.")
                if not ui.confirm("Try again with a different key?"):
                    return
                continue
            
            break
        
        # Get key description
        key_description = ui.prompt_input("Enter a description for this key:")
        
        # Add the key
        try:
            key_info = {
                "type": key_type,
                "value": key_value,
                "description": key_description,
                "registration_date": self._get_current_date(),
                "machine_id": self.machine_id
            }
            
            self._add_key_to_store(key_info)
            ui.display_success(f"Developer key registered successfully")
            
        except Exception as e:
            ui.display_error(f"Error registering key: {str(e)}")
            self.logger.error(f"Key registration error: {str(e)}")
    
    def _view_keys(self, ui):
        """View registered developer keys"""
        ui.display_info("Registered developer keys:")
        
        try:
            keys = self._get_stored_keys()
            
            if not keys:
                ui.display_info("No keys are currently registered.")
                return
            
            for i, key in enumerate(keys):
                # Mask the key value for security
                masked_key = self._mask_key_value(key["value"])
                
                ui.display_info(f"\nKey #{i+1}:")
                ui.display_info(f"  Type: {self._get_key_type_display(key['type'])}")
                ui.display_info(f"  Value: {masked_key}")
                ui.display_info(f"  Description: {key['description']}")
                ui.display_info(f"  Registration Date: {key['registration_date']}")
            
        except Exception as e:
            ui.display_error(f"Error retrieving keys: {str(e)}")
            self.logger.error(f"Key retrieval error: {str(e)}")
    
    def _validate_key(self, ui):
        """Validate a developer key"""
        ui.display_info("Validating developer key...")
        
        # Get key value
        key_value = ui.prompt_input("Enter the key to validate:")
        
        # Attempt to validate
        ui.display_info("Validating key format and registration status...")
        
        try:
            # Check if the key format is valid for any known type
            key_type = None
            for ktype, pattern in self.KEY_PATTERNS.items():
                if pattern.match(key_value):
                    key_type = ktype
                    break
            
            if not key_type:
                ui.display_error("Invalid key format. This does not match any supported key type.")
                return
            
            # Check if the key is registered
            is_registered = self._key_exists(key_value)
            
            if is_registered:
                ui.display_success(f"Key validation successful")
                ui.display_info(f"Key type: {self._get_key_type_display(key_type)}")
                ui.display_info("This key is properly registered in the system.")
            else:
                ui.display_warning(f"Key format is valid ({self._get_key_type_display(key_type)})")
                ui.display_warning("However, this key is not registered in the system.")
                
                if ui.confirm("Would you like to register this key now?"):
                    # Pre-fill the key value and redirect to registration
                    key_description = ui.prompt_input("Enter a description for this key:")
                    
                    key_info = {
                        "type": key_type,
                        "value": key_value,
                        "description": key_description,
                        "registration_date": self._get_current_date(),
                        "machine_id": self.machine_id
                    }
                    
                    self._add_key_to_store(key_info)
                    ui.display_success(f"Developer key registered successfully")
            
        except Exception as e:
            ui.display_error(f"Error validating key: {str(e)}")
            self.logger.error(f"Key validation error: {str(e)}")
    
    def _remove_key(self, ui):
        """Remove a registered developer key"""
        ui.display_info("Removing developer key...")
        
        try:
            keys = self._get_stored_keys()
            
            if not keys:
                ui.display_info("No keys are currently registered.")
                return
            
            # Create display options for each key
            key_options = []
            for key in keys:
                masked_key = self._mask_key_value(key["value"])
                key_options.append(f"{self._get_key_type_display(key['type'])}: {masked_key} ({key['description']})")
            
            # Let user select a key to remove
            key_idx = ui.prompt_choice("Select key to remove:", key_options)
            
            # Confirm removal
            if not ui.confirm(f"Are you sure you want to remove this key?"):
                ui.display_info("Key removal cancelled.")
                return
            
            # Remove the key
            removed_key = keys.pop(key_idx)
            self._save_keys(keys)
            
            ui.display_success(f"Developer key removed successfully")
            
        except Exception as e:
            ui.display_error(f"Error removing key: {str(e)}")
            self.logger.error(f"Key removal error: {str(e)}")
    
    def _validate_key_format(self, key_type: str, key_value: str) -> bool:
        """Validate the format of a key"""
        if key_type not in self.KEY_PATTERNS:
            return False
        
        return bool(self.KEY_PATTERNS[key_type].match(key_value))
    
    def _key_exists(self, key_value: str) -> bool:
        """Check if a key already exists in the store"""
        keys = self._get_stored_keys()
        return any(key["value"] == key_value for key in keys)
    
    def _get_stored_keys(self) -> List[Dict[str, Any]]:
        """Get all stored keys"""
        try:
            # Get registry values
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, self.REG_KEY_PATH, 0, 
                              winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as key:
                encrypted_data = winreg.QueryValueEx(key, self.REG_KEY_STORE_VALUE)[0]
                salt = winreg.QueryValueEx(key, self.REG_KEY_SALT_VALUE)[0]
            
            # Decrypt the data
            decrypted_data = self._decrypt_data(encrypted_data, salt)
            
            # Parse JSON
            return json.loads(decrypted_data)
            
        except FileNotFoundError:
            # Registry key doesn't exist yet
            return []
        except Exception as e:
            self.logger.error(f"Error retrieving stored keys: {str(e)}")
            return []
    
    def _add_key_to_store(self, key_info: Dict[str, Any]):
        """Add a key to the secure store"""
        # Get existing keys
        keys = self._get_stored_keys()
        
        # Add new key
        keys.append(key_info)
        
        # Save updated keys
        self._save_keys(keys)
    
    def _save_keys(self, keys: List[Dict[str, Any]]):
        """Save keys to the secure store"""
        try:
            # Generate salt if not existing
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, self.REG_KEY_PATH, 0, 
                                  winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as key:
                    salt = winreg.QueryValueEx(key, self.REG_KEY_SALT_VALUE)[0]
            except FileNotFoundError:
                # Create new salt
                salt = secrets.token_bytes(16)
            
            # Serialize and encrypt data
            json_data = json.dumps(keys, indent=2)
            encrypted_data = self._encrypt_data(json_data, salt)
            
            # Save to registry
            with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, self.REG_KEY_PATH) as key:
                winreg.SetValueEx(key, self.REG_KEY_STORE_VALUE, 0, winreg.REG_BINARY, encrypted_data)
                winreg.SetValueEx(key, self.REG_KEY_SALT_VALUE, 0, winreg.REG_BINARY, salt)
                
        except Exception as e:
            self.logger.error(f"Error saving keys: {str(e)}")
            raise
    
    def _encrypt_data(self, data: str, salt: bytes) -> bytes:
        """Encrypt data using Fernet symmetric encryption"""
        password = self._get_encryption_password().encode()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        f = Fernet(key)
        return f.encrypt(data.encode())
    
    def _decrypt_data(self, encrypted_data: bytes, salt: bytes) -> str:
        """Decrypt data using Fernet symmetric encryption"""
        password = self._get_encryption_password().encode()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        f = Fernet(key)
        return f.decrypt(encrypted_data).decode()
    
    def _get_encryption_password(self) -> str:
        """Get encryption password based on unique machine characteristics"""
        # This combines machine ID with a salt
        # In a real implementation, this would be much more secure
        return f"DevToolKit-{self.machine_id}-KeyProtection"
    
    def _get_machine_id(self) -> str:
        """Get a unique identifier for this machine"""
        try:
            # Combine various system identifiers
            import wmi
            c = wmi.WMI()
            
            system_info = {}
            
            # Get BIOS serial
            for bios in c.Win32_BIOS():
                system_info['bios_serial'] = bios.SerialNumber
            
            # Get processor ID
            for cpu in c.Win32_Processor():
                system_info['processor_id'] = cpu.ProcessorId
            
            # Get disk serial
            for disk in c.Win32_DiskDrive():
                if disk.SerialNumber:
                    system_info['disk_serial'] = disk.SerialNumber
                    break
            
            # Create a combined hash
            combined = "-".join(str(val) for val in system_info.values())
            return hashlib.sha256(combined.encode()).hexdigest()[:16]
            
        except Exception as e:
            self.logger.error(f"Error getting machine ID: {str(e)}")
            # Fallback to a less unique but still useful ID
            import socket
            return hashlib.md5(socket.gethostname().encode()).hexdigest()[:16]
    
    def _get_current_date(self) -> str:
        """Get current date in a standardized format"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _mask_key_value(self, key_value: str) -> str:
        """Mask key value for display (show only first and last 4 chars)"""
        if len(key_value) <= 8:
            return "*" * len(key_value)
        
        return key_value[:4] + "*" * (len(key_value) - 8) + key_value[-4:]
    
    def _get_key_type_display(self, key_type: str) -> str:
        """Get user-friendly display name for key type"""
        type_display = {
            "windows_dev": "Windows Developer Key",
            "enterprise": "Enterprise Developer Key",
            "visual_studio": "Visual Studio Key"
        }
        return type_display.get(key_type, key_type)