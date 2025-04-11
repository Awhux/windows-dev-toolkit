"""
Feature Detection and Caching Utility

This module provides functionality for detecting Windows features,
caching detection results, and optimizing performance through pattern matching.
"""
import os
import re
import json
import logging
import subprocess
import winreg
import hashlib
from typing import Dict, Any, List, Set, Optional, Tuple, Pattern, Match
from datetime import datetime, timedelta

class FeatureDetection:
    """
    Handles detection of Windows features, tools, and configurations.
    Implements caching and regex pattern matching for efficient feature detection.
    """
    
    # Cache settings
    CACHE_DIR = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), 
                            'YourCompany', 'DevToolkit', 'cache')
    CACHE_FILENAME = 'feature_cache.json'
    CACHE_EXPIRY = 24  # hours
    
    # Regex patterns for feature detection
    PATTERNS = {
        # Windows Feature detection patterns
        'windows_features': {
            'installed': re.compile(r'State\s+:\s+(\d+)\s+Enabled'),
            'available': re.compile(r'Feature Name\s+:\s+(.+)'),
        },
        
        # Software detection patterns
        'software': {
            'git': re.compile(r'git version\s+(.+)'),
            'node': re.compile(r'v(\d+\.\d+\.\d+)'),
            'npm': re.compile(r'(\d+\.\d+\.\d+)'),
            'python': re.compile(r'Python\s+(\d+\.\d+\.\d+)'),
            'dotnet': re.compile(r'(\d+\.\d+\.\d+)'),
            'vs': re.compile(r'Visual Studio.+(\d{4})'),
            'vscode': re.compile(r'(\d+\.\d+\.\d+)'),
        },
        
        # Registry patterns
        'registry': {
            'dev_mode': re.compile(r'AppModelUnlock'),
            'windows_version': re.compile(r'ProductName\s+Windows\s+(\d+)'),
            'build_number': re.compile(r'CurrentBuildNumber\s+(\d+)'),
        },
        
        # Office patterns
        'office': {
            'office_installed': re.compile(r'Microsoft Office (\d{4})'),
            'office_path': re.compile(r'InstallPath\s+REG_SZ\s+(.+)'),
            'office_product_ids': re.compile(r'ProductReleaseIds\s+REG_SZ\s+(.+)'),
        },
        
        # Hardware patterns
        'hardware': {
            'processor': re.compile(r'Intel|AMD|Arm'),
            'ram': re.compile(r'(\d+)GB'),
            'disk': re.compile(r'(\d+)GB'),
        }
    }
    
    def __init__(self):
        """Initialize the feature detection utility"""
        self.logger = logging.getLogger('feature_detection')
        self._ensure_cache_dir()
        self.cache = self._load_cache()
    
    def detect_windows_features(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Detect installed Windows features
        
        Args:
            force_refresh: Force a refresh of cached data
            
        Returns:
            Dictionary of detected Windows features
        """
        cache_key = 'windows_features'
        
        # Check cache first unless force refresh
        if not force_refresh and cache_key in self.cache:
            if not self._is_cache_expired(self.cache[cache_key]['timestamp']):
                self.logger.debug(f"Using cached {cache_key} data")
                return self.cache[cache_key]['data']
        
        self.logger.info(f"Detecting Windows features (forced={force_refresh})")
        
        # Run detection command
        features = {}
        try:
            # Get list of all features
            result = subprocess.run(
                ['dism', '/online', '/get-features', '/format:table'], 
                capture_output=True, 
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                self.logger.error(f"Error detecting Windows features: {result.stderr}")
                return features
            
            # Parse output with regex
            feature_pattern = self.PATTERNS['windows_features']['available']
            state_pattern = self.PATTERNS['windows_features']['installed']
            
            # Extract feature names
            all_features = feature_pattern.findall(result.stdout)
            
            # Check state for each feature
            for feature in all_features:
                feature_name = feature.strip()
                # Get detailed info for this feature
                detail_result = subprocess.run(
                    ['dism', '/online', '/get-featureinfo', f'/featurename:{feature_name}'],
                    capture_output=True,
                    text=True,
                    check=False
                )
                
                # Parse state
                if detail_result.returncode == 0:
                    state_match = state_pattern.search(detail_result.stdout)
                    if state_match and state_match.group(1) == '1':
                        features[feature_name] = {
                            'installed': True,
                            'details': self._extract_feature_details(detail_result.stdout)
                        }
                    else:
                        features[feature_name] = {
                            'installed': False,
                            'details': self._extract_feature_details(detail_result.stdout)
                        }
            
            # Update cache
            self._update_cache(cache_key, features)
            
            return features
            
        except Exception as e:
            self.logger.error(f"Error detecting Windows features: {str(e)}")
            return features
    
    def detect_installed_software(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Detect installed developer software
        
        Args:
            force_refresh: Force a refresh of cached data
            
        Returns:
            Dictionary of detected software with version info
        """
        cache_key = 'installed_software'
        
        # Check cache first unless force refresh
        if not force_refresh and cache_key in self.cache:
            if not self._is_cache_expired(self.cache[cache_key]['timestamp']):
                self.logger.debug(f"Using cached {cache_key} data")
                return self.cache[cache_key]['data']
        
        self.logger.info(f"Detecting installed software (forced={force_refresh})")
        
        # Run detection for various software
        software = {}
        
        # Detect Git
        try:
            result = subprocess.run(['git', '--version'], capture_output=True, text=True, check=False)
            if result.returncode == 0:
                match = self.PATTERNS['software']['git'].search(result.stdout)
                if match:
                    software['git'] = {'installed': True, 'version': match.group(1)}
        except Exception:
            software['git'] = {'installed': False}
        
        # Detect Node.js
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True, check=False)
            if result.returncode == 0:
                match = self.PATTERNS['software']['node'].search(result.stdout)
                if match:
                    software['node'] = {'installed': True, 'version': match.group(1)}
        except Exception:
            software['node'] = {'installed': False}
        
        # Detect npm
        try:
            result = subprocess.run(['npm', '--version'], capture_output=True, text=True, check=False)
            if result.returncode == 0:
                match = self.PATTERNS['software']['npm'].search(result.stdout)
                if match:
                    software['npm'] = {'installed': True, 'version': match.group(1)}
        except Exception:
            software['npm'] = {'installed': False}
        
        # Detect Python
        try:
            result = subprocess.run(['python', '--version'], capture_output=True, text=True, check=False)
            if result.returncode == 0:
                match = self.PATTERNS['software']['python'].search(result.stdout)
                if match:
                    software['python'] = {'installed': True, 'version': match.group(1)}
        except Exception:
            software['python'] = {'installed': False}
        
        # Detect .NET
        try:
            result = subprocess.run(['dotnet', '--version'], capture_output=True, text=True, check=False)
            if result.returncode == 0:
                match = self.PATTERNS['software']['dotnet'].search(result.stdout)
                if match:
                    software['dotnet'] = {'installed': True, 'version': match.group(1)}
        except Exception:
            software['dotnet'] = {'installed': False}
        
        # Detect Visual Studio (using registry)
        try:
            vs_versions = self._detect_visual_studio_versions()
            if vs_versions:
                software['visual_studio'] = {'installed': True, 'versions': vs_versions}
            else:
                software['visual_studio'] = {'installed': False}
        except Exception:
            software['visual_studio'] = {'installed': False}
        
        # Detect VS Code (using where command)
        try:
            result = subprocess.run(['where', 'code'], capture_output=True, text=True, check=False)
            if result.returncode == 0:
                software['vscode'] = {'installed': True, 'path': result.stdout.strip()}
                # Try to get version
                version_result = subprocess.run(['code', '--version'], capture_output=True, text=True, check=False)
                if version_result.returncode == 0:
                    version_lines = version_result.stdout.strip().split('\n')
                    if version_lines:
                        software['vscode']['version'] = version_lines[0]
            else:
                software['vscode'] = {'installed': False}
        except Exception:
            software['vscode'] = {'installed': False}
        
        # Update cache
        self._update_cache(cache_key, software)
        
        return software
    
    def detect_system_configuration(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Detect system configuration including OS details
        
        Args:
            force_refresh: Force a refresh of cached data
            
        Returns:
            Dictionary of system configuration details
        """
        cache_key = 'system_configuration'
        
        # Check cache first unless force refresh
        if not force_refresh and cache_key in self.cache:
            if not self._is_cache_expired(self.cache[cache_key]['timestamp']):
                self.logger.debug(f"Using cached {cache_key} data")
                return self.cache[cache_key]['data']
        
        self.logger.info(f"Detecting system configuration (forced={force_refresh})")
        
        # Collect system information
        sys_config = {}
        
        # Get Windows version
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                              r'SOFTWARE\Microsoft\Windows NT\CurrentVersion') as key:
                
                # Get product name
                try:
                    value, _ = winreg.QueryValueEx(key, 'ProductName')
                    sys_config['os_name'] = value
                    
                    # Extract Windows version using regex
                    match = self.PATTERNS['registry']['windows_version'].search(value)
                    if match:
                        sys_config['windows_version'] = match.group(1)
                except Exception:
                    pass
                
                # Get build number
                try:
                    value, _ = winreg.QueryValueEx(key, 'CurrentBuildNumber')
                    sys_config['build_number'] = value
                except Exception:
                    pass
                
                # Get display version (like 21H2)
                try:
                    value, _ = winreg.QueryValueEx(key, 'DisplayVersion')
                    sys_config['display_version'] = value
                except Exception:
                    pass
        except Exception as e:
            self.logger.error(f"Error getting Windows version: {str(e)}")
        
        # Check if developer mode is enabled
        try:
            sys_config['developer_mode'] = self._is_dev_mode_enabled()
        except Exception as e:
            self.logger.error(f"Error checking developer mode: {str(e)}")
            sys_config['developer_mode'] = False
        
        # Get CPU and memory info
        try:
            system_info = self._get_system_info()
            sys_config.update(system_info)
        except Exception as e:
            self.logger.error(f"Error getting system info: {str(e)}")
        
        # Update cache
        self._update_cache(cache_key, sys_config)
        
        return sys_config
    
    def detect_office_installation(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Detect Microsoft Office installation details
        
        Args:
            force_refresh: Force a refresh of cached data
            
        Returns:
            Dictionary of Office installation details
        """
        cache_key = 'office_installation'
        
        # Check cache first unless force refresh
        if not force_refresh and cache_key in self.cache:
            if not self._is_cache_expired(self.cache[cache_key]['timestamp']):
                self.logger.debug(f"Using cached {cache_key} data")
                return self.cache[cache_key]['data']
        
        self.logger.info(f"Detecting Office installation (forced={force_refresh})")
        
        office_info = {'installed': False}
        
        # Check registry for Office installations
        try:
            # Check common Office registry paths
            office_paths = [
                # Office 365, 2019, 2021, LTSC
                r'SOFTWARE\Microsoft\Office\ClickToRun\Configuration',
                # Office 2016
                r'SOFTWARE\Microsoft\Office\16.0\Common\InstallRoot',
                # Office 2013
                r'SOFTWARE\Microsoft\Office\15.0\Common\InstallRoot',
                # Office 2010
                r'SOFTWARE\Microsoft\Office\14.0\Common\InstallRoot',
            ]
            
            for path in office_paths:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path) as key:
                        # For ClickToRun, check ProductReleaseIds
                        if 'ClickToRun' in path:
                            try:
                                value, _ = winreg.QueryValueEx(key, 'ProductReleaseIds')
                                office_info['installed'] = True
                                office_info['edition'] = value
                                
                                # Check channel
                                try:
                                    channel, _ = winreg.QueryValueEx(key, 'UpdateChannel')
                                    office_info['update_channel'] = channel
                                    
                                    # Detect if LTSC
                                    if 'PerpetualVL' in channel:
                                        office_info['is_ltsc'] = True
                                    else:
                                        office_info['is_ltsc'] = False
                                except Exception:
                                    pass
                                
                                break
                            except Exception:
                                pass
                        
                        # For traditional Office, check InstallPath
                        else:
                            try:
                                value, _ = winreg.QueryValueEx(key, 'Path')
                                office_info['installed'] = True
                                office_info['path'] = value
                                
                                # Try to determine version
                                if '16.0' in path:
                                    office_info['version'] = '2016'
                                elif '15.0' in path:
                                    office_info['version'] = '2013'
                                elif '14.0' in path:
                                    office_info['version'] = '2010'
                                
                                break
                            except Exception:
                                pass
                except Exception:
                    continue
            
            # If Office is installed, try to get more details
            if office_info['installed']:
                # Try to determine if volume license
                try:
                    result = subprocess.run(
                        ['cscript', '//nologo', os.path.join(os.environ['ProgramFiles(x86)'], 
                                                           'Microsoft Office', 'Office16', 
                                                           'OSPP.VBS'), '/dstatus'],
                        capture_output=True,
                        text=True,
                        check=False
                    )
                    
                    if 'VOLUME_KMSCLIENT' in result.stdout:
                        office_info['license_type'] = 'volume'
                    elif 'RETAIL' in result.stdout:
                        office_info['license_type'] = 'retail'
                except Exception:
                    pass
        
        except Exception as e:
            self.logger.error(f"Error detecting Office installation: {str(e)}")
        
        # Update cache
        self._update_cache(cache_key, office_info)
        
        return office_info
    
    def get_all_features(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get comprehensive information about all detectable features
        
        Args:
            force_refresh: Force a refresh of all cached data
            
        Returns:
            Consolidated dictionary of all feature detection results
        """
        self.logger.info(f"Getting all features (forced={force_refresh})")
        
        all_features = {
            'system': self.detect_system_configuration(force_refresh),
            'windows_features': self.detect_windows_features(force_refresh),
            'software': self.detect_installed_software(force_refresh),
            'office': self.detect_office_installation(force_refresh),
            'timestamp': datetime.now().isoformat()
        }
        
        return all_features
    
    def clear_cache(self) -> None:
        """Clear all cached detection data"""
        self.logger.info("Clearing feature detection cache")
        
        self.cache = {}
        
        # Remove cache file
        cache_path = os.path.join(self.CACHE_DIR, self.CACHE_FILENAME)
        if os.path.exists(cache_path):
            try:
                os.remove(cache_path)
                self.logger.debug(f"Removed cache file: {cache_path}")
            except Exception as e:
                self.logger.error(f"Error removing cache file: {str(e)}")
    
    def _ensure_cache_dir(self) -> None:
        """Ensure cache directory exists"""
        if not os.path.exists(self.CACHE_DIR):
            try:
                os.makedirs(self.CACHE_DIR, exist_ok=True)
                self.logger.debug(f"Created cache directory: {self.CACHE_DIR}")
            except Exception as e:
                self.logger.error(f"Error creating cache directory: {str(e)}")
    
    def _load_cache(self) -> Dict[str, Any]:
        """Load cache from disk"""
        cache_path = os.path.join(self.CACHE_DIR, self.CACHE_FILENAME)
        
        if not os.path.exists(cache_path):
            return {}
        
        try:
            with open(cache_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading cache: {str(e)}")
            return {}
    
    def _save_cache(self) -> None:
        """Save cache to disk"""
        cache_path = os.path.join(self.CACHE_DIR, self.CACHE_FILENAME)
        
        try:
            with open(cache_path, 'w') as f:
                json.dump(self.cache, f, indent=2)
                
            self.logger.debug(f"Cache saved to: {cache_path}")
        except Exception as e:
            self.logger.error(f"Error saving cache: {str(e)}")
    
    def _update_cache(self, key: str, data: Dict[str, Any]) -> None:
        """Update cache with new data"""
        self.cache[key] = {
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        
        # Save updated cache
        self._save_cache()
    
    def _is_cache_expired(self, timestamp_str: str) -> bool:
        """Check if cache entry has expired"""
        try:
            timestamp = datetime.fromisoformat(timestamp_str)
            expiry = datetime.now() - timedelta(hours=self.CACHE_EXPIRY)
            
            return timestamp < expiry
        except Exception:
            # If we can't parse the timestamp, consider it expired
            return True
    
    def _extract_feature_details(self, output: str) -> Dict[str, str]:
        """Extract detailed feature information from DISM output"""
        details = {}
        lines = output.strip().split('\n')
        
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                details[key.strip()] = value.strip()
        
        return details
    
    def _detect_visual_studio_versions(self) -> List[Dict[str, str]]:
        """Detect installed Visual Studio versions"""
        vs_versions = []
        
        try:
            # Check Common7 paths for different VS versions
            base_paths = [
                os.environ.get('ProgramFiles(x86)', r'C:\Program Files (x86)'),
                os.environ.get('ProgramFiles', r'C:\Program Files')
            ]
            
            for base in base_paths:
                vs_root = os.path.join(base, 'Microsoft Visual Studio')
                
                if not os.path.exists(vs_root):
                    continue
                
                # Check for different year versions
                for year_dir in ['2022', '2019', '2017', '2015']:
                    vs_year_path = os.path.join(vs_root, year_dir)
                    
                    if not os.path.exists(vs_year_path):
                        continue
                    
                    # Check for different editions
                    for edition in ['Enterprise', 'Professional', 'Community']:
                        edition_path = os.path.join(vs_year_path, edition)
                        
                        if os.path.exists(edition_path):
                            # Check for Common7 dir to confirm it's a VS installation
                            if os.path.exists(os.path.join(edition_path, 'Common7')):
                                vs_versions.append({
                                    'year': year_dir,
                                    'edition': edition,
                                    'path': edition_path
                                })
            
            return vs_versions
        
        except Exception as e:
            self.logger.error(f"Error detecting Visual Studio: {str(e)}")
            return []
    
    def _is_dev_mode_enabled(self) -> bool:
        """Check if Windows Developer Mode is enabled"""
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                              r'SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock') as key:
                value, _ = winreg.QueryValueEx(key, 'AllowDevelopmentWithoutDevLicense')
                return value == 1
        except Exception:
            return False
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system hardware and configuration information"""
        info = {}
        
        try:
            # Use WMI to get system information
            import wmi
            c = wmi.WMI()
            
            # Get CPU info
            for cpu in c.Win32_Processor():
                info['cpu'] = {
                    'name': cpu.Name,
                    'cores': cpu.NumberOfCores,
                    'logical_processors': cpu.NumberOfLogicalProcessors,
                    'architecture': cpu.AddressWidth,  # 32 or 64 bit
                    'max_clock': cpu.MaxClockSpeed
                }
                break  # Just get the first CPU
            
            # Get memory info
            for mem in c.Win32_ComputerSystem():
                total_ram_gb = round(int(mem.TotalPhysicalMemory) / (1024**3), 2)
                info['ram'] = {
                    'total_gb': total_ram_gb
                }
                break
            
            # Get disk info
            drives = []
            for disk in c.Win32_LogicalDisk(DriveType=3):  # Type 3 = Local Disk
                drives.append({
                    'drive': disk.DeviceID,
                    'volume_name': disk.VolumeName,
                    'size_gb': round(int(disk.Size) / (1024**3), 2),
                    'free_gb': round(int(disk.FreeSpace) / (1024**3), 2)
                })
            info['drives'] = drives
            
            # Get operating system info
            for os in c.Win32_OperatingSystem():
                info['os'] = {
                    'name': os.Caption,
                    'version': os.Version,
                    'build': os.BuildNumber,
                    'architecture': os.OSArchitecture
                }
                break
            
            return info
            
        except Exception as e:
            self.logger.error(f"Error getting system info: {str(e)}")
            return {}