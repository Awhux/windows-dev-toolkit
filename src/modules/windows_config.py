"""
Windows Configuration Manager

This module handles Windows development environment configurations
for professional development teams using legitimate approaches.
"""
import os
import subprocess
import logging
import json
import winreg
from typing import Dict, Any, List, Optional

class WindowsConfigManager:
    """
    Manages Windows configurations for development environments
    using legitimate Windows features and APIs.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("windows_config")
    
    def execute(self, ui):
        """Main execution flow for Windows configuration"""
        options = [
            "Enable Developer Mode",
            "Configure Windows Features for Development",
            "Optimize System Performance",
            "Configure Windows Defender Exceptions",
            "Back to main menu"
        ]
        
        while True:
            choice = ui.display_menu("Windows Configuration", options)
            
            if choice == 4:  # Back to main menu
                break
            elif choice == 0:
                self._enable_developer_mode(ui)
            elif choice == 1:
                self._configure_windows_features(ui)
            elif choice == 2:
                self._optimize_system(ui)
            elif choice == 3:
                self._configure_defender(ui)
    
    def _enable_developer_mode(self, ui):
        """Enable Windows Developer Mode through legitimate registry settings"""
        ui.display_info("Enabling Windows Developer Mode...")
        
        try:
            # Confirm with user
            if not ui.confirm("This will enable Developer Mode on Windows. Continue?"):
                ui.display_info("Operation cancelled")
                return
            
            # Set registry keys for Developer Mode
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock"
            
            with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                winreg.SetValueEx(key, "AllowDevelopmentWithoutDevLicense", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "AllowAllTrustedApps", 0, winreg.REG_DWORD, 1)
            
            ui.display_success("Developer Mode enabled successfully")
            ui.display_info("You may need to restart your computer for changes to take effect")
            
        except Exception as e:
            ui.display_error(f"Error enabling Developer Mode: {str(e)}")
            self.logger.error(f"Developer Mode error: {str(e)}")
    
    def _configure_windows_features(self, ui):
        """Configure Windows Features for development"""
        ui.display_info("Configuring Windows Features for development...")
        
        # Define development-related Windows features
        features = [
            ("Microsoft-Windows-Subsystem-Linux", "Windows Subsystem for Linux (WSL)"),
            ("VirtualMachinePlatform", "Virtual Machine Platform (for WSL2)"),
            ("NetFx3", ".NET Framework 3.5"),
            ("NetFx4-AdvSrvs", ".NET Framework 4.8 Advanced Services"),
            ("IIS-WebServerRole", "Internet Information Services (IIS)"),
            ("HypervisorPlatform", "Hyper-V Platform"),
            ("Containers", "Windows Containers"),
            ("Microsoft-Hyper-V-All", "Hyper-V"),
            ("Microsoft-Windows-NetFx3-OC-Package", ".NET Framework 3.5 (includes 2.0 and 3.0)")
        ]
        
        # Let user select features to install
        feature_names = [f[1] for f in features]
        selected_indices = ui.prompt_multichoice("Select features to install:", feature_names)
        
        if not selected_indices:
            ui.display_info("No features selected")
            return
            
        # Confirm with user
        selected_features = [features[i][0] for i in selected_indices]
        selected_names = [features[i][1] for i in selected_indices]
        
        ui.display_info("You selected the following features:")
        for name in selected_names:
            ui.display_info(f"- {name}")
            
        if not ui.confirm("Install these Windows Features? This may require a restart."):
            ui.display_info("Operation cancelled")
            return
        
        # Install selected features
        for feature in selected_features:
            ui.display_info(f"Installing: {feature}")
            
            try:
                result = subprocess.run(
                    ["dism", "/online", "/enable-feature", f"/featurename:{feature}", "/all", "/norestart"],
                    capture_output=True,
                    text=True,
                    check=False
                )
                
                if result.returncode == 0:
                    ui.display_success(f"Successfully installed {feature}")
                else:
                    ui.display_error(f"Failed to install {feature}: {result.stderr}")
                    
            except Exception as e:
                ui.display_error(f"Error installing {feature}: {str(e)}")
                self.logger.error(f"Feature installation error: {str(e)}")
        
        ui.display_info("Feature installation completed")
        ui.display_warning("Some changes may require a system restart to take effect")
    
    def _optimize_system(self, ui):
        """Optimize system performance for development work"""
        ui.display_info("Optimizing system for development...")
        
        optimizations = [
            "Adjust for best performance of: Programs",
            "Disable unnecessary visual effects",
            "Configure power settings for high performance",
            "Adjust virtual memory settings",
            "Set proper pagefile size"
        ]
        
        selected_indices = ui.prompt_multichoice("Select optimizations to apply:", optimizations)
        
        if not selected_indices:
            ui.display_info("No optimizations selected")
            return
            
        # Confirm with user
        if not ui.confirm("Apply selected system optimizations?"):
            ui.display_info("Operation cancelled")
            return
        
        # Apply optimizations
        for idx in selected_indices:
            if idx == 0:  # Performance for programs
                self._set_performance_programs(ui)
            elif idx == 1:  # Visual effects
                self._disable_visual_effects(ui)
            elif idx == 2:  # Power settings
                self._set_power_high_performance(ui)
            elif idx == 3:  # Virtual memory
                self._configure_virtual_memory(ui)
            elif idx == 4:  # Pagefile
                self._configure_pagefile(ui)
                
        ui.display_success("System optimizations applied")
    
    def _set_performance_programs(self, ui):
        """Set system for best performance of programs"""
        try:
            key_path = r"SYSTEM\CurrentControlSet\Control\PriorityControl"
            with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                winreg.SetValueEx(key, "Win32PrioritySeparation", 0, winreg.REG_DWORD, 2)
                
            ui.display_success("System adjusted for best program performance")
            
        except Exception as e:
            ui.display_error(f"Error setting performance priority: {str(e)}")
            self.logger.error(f"Performance priority error: {str(e)}")
    
    def _disable_visual_effects(self, ui):
        """Disable unnecessary visual effects"""
        try:
            # Set visual effects for performance
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects"
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                winreg.SetValueEx(key, "VisualFXSetting", 0, winreg.REG_DWORD, 2)
                
            # Advanced system settings
            key_path = r"Control Panel\Desktop"
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                winreg.SetValueEx(key, "UserPreferencesMask", 0, winreg.REG_BINARY, b"\x90\x12\x01\x80")
                
            ui.display_success("Visual effects optimized for performance")
            ui.display_info("Some changes may require logging out and back in to take effect")
            
        except Exception as e:
            ui.display_error(f"Error setting visual effects: {str(e)}")
            self.logger.error(f"Visual effects error: {str(e)}")
    
    def _set_power_high_performance(self, ui):
        """Set power plan to high performance"""
        try:
            # Set high performance power plan
            result = subprocess.run(
                ["powercfg", "/setactive", "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                ui.display_success("Power plan set to High Performance")
            else:
                # Try to create and set high performance plan
                create_result = subprocess.run(
                    ["powercfg", "-duplicatescheme", "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"],
                    capture_output=True,
                    text=True,
                    check=False
                )
                
                if create_result.returncode == 0:
                    # Extract the GUID of the created plan
                    import re
                    match = re.search(r"([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})", create_result.stdout)
                    if match:
                        guid = match.group(1)
                        # Set the created plan as active
                        subprocess.run(["powercfg", "/setactive", guid], check=False)
                        ui.display_success("Created and set High Performance power plan")
                    else:
                        ui.display_error("Failed to extract power plan GUID")
                else:
                    ui.display_error(f"Failed to create High Performance power plan: {create_result.stderr}")
                
        except Exception as e:
            ui.display_error(f"Error setting power plan: {str(e)}")
            self.logger.error(f"Power plan error: {str(e)}")
    
    def _configure_virtual_memory(self, ui):
        """Configure virtual memory settings"""
        # This would typically be implemented with registry changes
        # but that's complex and system-specific, so we'll just show guidance
        ui.display_info("Virtual memory configuration guide:")
        ui.display_info("1. Open System Properties (sysdm.cpl)")
        ui.display_info("2. Go to Advanced tab")
        ui.display_info("3. Click Settings under Performance")
        ui.display_info("4. Go to Advanced tab")
        ui.display_info("5. Click Change under Virtual memory")
        ui.display_info("6. Configure according to development needs")
        
        ui.display_warning("This setting requires manual configuration")
    
    def _configure_pagefile(self, ui):
        """Configure pagefile size"""
        # Similar to virtual memory, this is complex and system-specific
        ui.display_info("For optimal development performance, set pagefile size to:")
        ui.display_info("- Initial size: RAM amount in MB")
        ui.display_info("- Maximum size: 2x RAM amount in MB")
        
        # Show system RAM
        try:
            import psutil
            ram_gb = round(psutil.virtual_memory().total / (1024**3), 2)
            ui.display_info(f"Your system has approximately {ram_gb} GB of RAM")
            ui.display_info(f"Recommended pagefile: Initial {int(ram_gb*1024)} MB, Max {int(ram_gb*1024*2)} MB")
        except ImportError:
            ui.display_info("Install psutil package to get RAM recommendations")
            
        ui.display_warning("This setting requires manual configuration")
    
    def _configure_defender(self, ui):
        """Configure Windows Defender exceptions for development folders"""
        ui.display_info("Configuring Windows Defender exceptions for development...")
        
        # Get development folders from user
        folders = []
        while True:
            folder = ui.prompt_input("Enter development folder path (leave empty to finish):")
            if not folder:
                break
                
            if os.path.exists(folder):
                folders.append(folder)
            else:
                ui.display_warning(f"Path does not exist: {folder}")
        
        if not folders:
            ui.display_info("No folders specified")
            return
            
        # Show selected folders and confirm
        ui.display_info("Adding these folders as Windows Defender exceptions:")
        for folder in folders:
            ui.display_info(f"- {folder}")
            
        if not ui.confirm("Add these folders as Windows Defender exceptions?"):
            ui.display_info("Operation cancelled")
            return
        
        # Add folders as exceptions
        for folder in folders:
            try:
                result = subprocess.run(
                    ["powershell", "-Command", f"Add-MpPreference -ExclusionPath '{folder}'"],
                    capture_output=True,
                    text=True,
                    check=False
                )
                
                if result.returncode == 0:
                    ui.display_success(f"Added exception for: {folder}")
                else:
                    ui.display_error(f"Failed to add exception for {folder}: {result.stderr}")
                    
            except Exception as e:
                ui.display_error(f"Error adding exception: {str(e)}")
                self.logger.error(f"Defender exception error: {str(e)}")
        
        ui.display_success("Windows Defender exceptions configured")