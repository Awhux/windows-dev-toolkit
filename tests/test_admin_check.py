"""
Tests for the admin_check utility module.
"""
import unittest
from unittest.mock import patch
import sys

# Add local path to import modules
sys.path.append('.')

from windows_dev_toolkit.utils.admin_check import verify_admin_privileges


class TestAdminCheck(unittest.TestCase):
    """Test cases for admin check functionality."""

    @patch('ctypes.windll.shell32.IsUserAnAdmin')
    def test_admin_check_admin(self, mock_is_admin):
        """Test admin check when running as admin."""
        # Mock the IsUserAnAdmin function to return True (admin)
        mock_is_admin.return_value = 1
        
        # Test the function
        result = verify_admin_privileges()
        
        # Verify the result
        self.assertTrue(result)
        mock_is_admin.assert_called_once()

    @patch('ctypes.windll.shell32.IsUserAnAdmin')
    def test_admin_check_non_admin(self, mock_is_admin):
        """Test admin check when not running as admin."""
        # Mock the IsUserAnAdmin function to return False (not admin)
        mock_is_admin.return_value = 0
        
        # Test the function
        result = verify_admin_privileges()
        
        # Verify the result
        self.assertFalse(result)
        mock_is_admin.assert_called_once()

    @patch('ctypes.windll.shell32.IsUserAnAdmin')
    def test_admin_check_exception(self, mock_is_admin):
        """Test admin check when an exception occurs."""
        # Mock the IsUserAnAdmin function to raise an exception
        mock_is_admin.side_effect = Exception("Test exception")
        
        # Test the function
        result = verify_admin_privileges()
        
        # The function should return False when an exception occurs
        self.assertFalse(result)
        mock_is_admin.assert_called_once()

    @patch('os.name', 'posix')
    def test_admin_check_non_windows(self):
        """Test admin check on non-Windows platform."""
        # Test the function on a non-Windows platform
        result = verify_admin_privileges()
        
        # The function should return False on non-Windows platforms
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()