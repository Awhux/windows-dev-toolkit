"""
Tests for the Windows Configuration Manager module.
"""
import unittest
from unittest.mock import patch, MagicMock, call
import sys
import os
import winreg

# Add local path to import modules
sys.path.append('.')

from windows_dev_toolkit.modules.windows_config import WindowsConfigManager


class TestWindowsConfigManager(unittest.TestCase):
    """Test cases for Windows Configuration Manager functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock config
        self.config = {
            "windows": {
                "features": ["Microsoft-Windows-Subsystem-Linux", "VirtualMachinePlatform"],
                "dev_mode": True
            }
        }
        
        # Create the manager instance
        self.windows_manager = WindowsConfigManager(self.config)
        
        # Create a mock UI
        self.mock_ui = MagicMock()

    @patch('winreg.CreateKey')
    @patch('winreg.SetValueEx')
    def test_enable_developer_mode(self, mock_set_value, mock_create_key):
        """Test enabling Windows Developer Mode."""
        # Set up mocks
        mock_key = MagicMock()
        mock_create_key.return_value.__enter__.return_value = mock_key
        
        # Set up UI for confirmation
        self.mock_ui.confirm.return_value = True
        
        # Call the enable developer mode method
        self.windows_manager._enable_developer_mode(self.mock_ui)
        
        # Verify confirmation was asked
        self.mock_ui.confirm.assert_called_once()
        
        # Verify registry key was created
        mock_create_key.assert_called_once_with(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock"
        )
        
        # Verify registry values were set
        mock_set_value.assert_has_calls([
            call(mock_key, "AllowDevelopmentWithoutDevLicense", 0, winreg.REG_DWORD, 1),
            call(mock_key, "AllowAllTrustedApps", 0, winreg.REG_DWORD, 1)
        ])
        
        # Verify UI methods were called
        self.mock_ui.display_info.assert_called()
        self.mock_ui.display_success.assert_called_once()

    @patch('subprocess.run')
    def test_configure_windows_features(self, mock_run):
        """Test configuring Windows features."""
        # Set up mock subprocess
        mock_run.return_value.returncode = 0
        
        # Set up UI for feature selection and confirmation
        self.mock_ui.prompt_multichoice.return_value = [0, 2]  # Select features 0 and 2
        self.mock_ui.confirm.return_value = True
        
        # Call the configure Windows features method
        self.windows_manager._configure_windows_features(self.mock_ui)
        
        # Verify feature selection was prompted
        self.mock_ui.prompt_multichoice.assert_called_once()
        
        # Verify confirmation was asked
        self.mock_ui.confirm.assert_called_once()
        
        # Verify subprocess.run was called for each feature
        self.assertEqual(mock_run.call_count, 2)
        
        # Verify UI methods were called
        self.mock_ui.display_info.assert_called()
        self.mock_ui.display_success.assert_called()

    @patch('winreg.CreateKey')
    @patch('winreg.SetValueEx')
    def test_set_performance_programs(self, mock_set_value, mock_create_key):
        """Test setting system for best performance of programs."""
        # Set up mocks
        mock_key = MagicMock()
        mock_create_key.return_value.__enter__.return_value = mock_key
        
        # Call the performance settings method
        self.windows_manager._set_performance_programs(self.mock_ui)
        
        # Verify registry key was created
        mock_create_key.assert_called_once_with(
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Control\PriorityControl"
        )
        
        # Verify registry value was set
        mock_set_value.assert_called_once_with(
            mock_key, "Win32PrioritySeparation", 0, winreg.REG_DWORD, 2
        )
        
        # Verify UI method was called
        self.mock_ui.display_success.assert_called_once()

    @patch('winreg.CreateKey')
    @patch('winreg.SetValueEx')
    def test_disable_visual_effects(self, mock_set_value, mock_create_key):
        """Test disabling visual effects for performance."""
        # Set up mocks
        mock_key = MagicMock()
        mock_create_key.return_value.__enter__.return_value = mock_key
        
        # Call the visual effects method
        self.windows_manager._disable_visual_effects(self.mock_ui)
        
        # Verify registry keys were created (2 different keys)
        self.assertEqual(mock_create_key.call_count, 2)
        
        # Verify registry values were set
        self.assertEqual(mock_set_value.call_count, 2)
        
        # Verify UI methods were called
        self.mock_ui.display_success.assert_called_once()
        self.mock_ui.display_info.assert_called_once()

    @patch('subprocess.run')
    def test_set_power_high_performance(self, mock_run):
        """Test setting power plan to high performance."""
        # First test: successful direct power plan set
        mock_run.return_value.returncode = 0
        
        # Call the power settings method
        self.windows_manager._set_power_high_performance(self.mock_ui)
        
        # Verify subprocess.run was called once
        self.assertEqual(mock_run.call_count, 1)
        
        # Verify UI method was called
        self.mock_ui.display_success.assert_called_once()
        
        # Reset mocks
        mock_run.reset_mock()
        self.mock_ui.reset_mock()
        
        # Second test: fallback to create and set
        mock_run.side_effect = [
            MagicMock(returncode=1),  # First call fails
            MagicMock(returncode=0, stdout="Power Scheme GUID: 12345678-1234-1234-1234-123456789abc"),  # Second succeeds
            MagicMock(returncode=0)  # Third succeeds
        ]
        
        # Call the power settings method
        self.windows_manager._set_power_high_performance(self.mock_ui)
        
        # Verify subprocess.run was called multiple times
        self.assertEqual(mock_run.call_count, 3)
        
        # Verify UI method was called
        self.mock_ui.display_success.assert_called_once()

    @patch('subprocess.run')
    def test_configure_defender(self, mock_run):
        """Test configuring Windows Defender exceptions."""
        # Set up mock subprocess
        mock_run.return_value.returncode = 0
        
        # Set up UI for folder input and confirmation
        self.mock_ui.prompt_input.side_effect = ["C:\\Dev\\Folder1", "C:\\Dev\\Folder2", ""]
        self.mock_ui.confirm.return_value = True
        
        # Mock path existence checks
        with patch('os.path.exists', return_value=True):
            # Call the configure defender method
            self.windows_manager._configure_defender(self.mock_ui)
        
        # Verify folder input was prompted multiple times
        self.assertEqual(self.mock_ui.prompt_input.call_count, 3)
        
        # Verify confirmation was asked
        self.mock_ui.confirm.assert_called_once()
        
        # Verify subprocess.run was called for each folder
        self.assertEqual(mock_run.call_count, 2)
        
        # Verify UI methods were called
        self.mock_ui.display_info.assert_called()
        self.mock_ui.display_success.assert_called()


if __name__ == '__main__':
    unittest.main()