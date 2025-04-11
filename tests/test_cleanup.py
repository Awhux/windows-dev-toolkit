"""
Tests for the cleanup utility module.
"""
import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import sys
import tempfile
import shutil

# Add local path to import modules
sys.path.append('.')

from windows_dev_toolkit.utils.cleanup import CleanupManager


class TestCleanupManager(unittest.TestCase):
    """Test cases for cleanup manager functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.cleanup_manager = CleanupManager()
        
        # Create temporary test directories and files
        self.test_dir = tempfile.mkdtemp()
        self.test_file = tempfile.NamedTemporaryFile(delete=False)
        self.test_file.close()

    def tearDown(self):
        """Tear down test fixtures."""
        # Clean up any remaining test files/directories
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        if os.path.exists(self.test_file.name):
            os.unlink(self.test_file.name)

    def test_add_temp_dir(self):
        """Test adding a temp directory to cleanup list."""
        # Add the temp directory
        self.cleanup_manager.add_temp_dir(self.test_dir)
        
        # Verify it was added to the list
        self.assertIn(self.test_dir, self.cleanup_manager.temp_dirs)

    def test_add_temp_file(self):
        """Test adding a temp file to cleanup list."""
        # Add the temp file
        self.cleanup_manager.add_temp_file(self.test_file.name)
        
        # Verify it was added to the list
        self.assertIn(self.test_file.name, self.cleanup_manager.temp_files)

    def test_run_cleanup_files(self):
        """Test running cleanup for files."""
        # Add the temp file
        self.cleanup_manager.add_temp_file(self.test_file.name)
        
        # Run cleanup
        self.cleanup_manager.run()
        
        # Verify the file was removed
        self.assertFalse(os.path.exists(self.test_file.name))
        
        # Verify the list was cleared
        self.assertEqual(len(self.cleanup_manager.temp_files), 0)

    def test_run_cleanup_directories(self):
        """Test running cleanup for directories."""
        # Add the temp directory
        self.cleanup_manager.add_temp_dir(self.test_dir)
        
        # Run cleanup
        self.cleanup_manager.run()
        
        # Verify the directory was removed
        self.assertFalse(os.path.exists(self.test_dir))
        
        # Verify the list was cleared
        self.assertEqual(len(self.cleanup_manager.temp_dirs), 0)

    @patch('os.remove')
    def test_cleanup_file_exception(self, mock_remove):
        """Test handling exceptions during file cleanup."""
        # Set up the mock to raise an exception
        mock_remove.side_effect = Exception("Test exception")
        
        # Add a file that will trigger the exception
        self.cleanup_manager.add_temp_file(self.test_file.name)
        
        # Run cleanup (should not raise an exception)
        self.cleanup_manager.run()
        
        # Verify the remove method was called
        mock_remove.assert_called_once_with(self.test_file.name)

    @patch('shutil.rmtree')
    def test_cleanup_directory_exception(self, mock_rmtree):
        """Test handling exceptions during directory cleanup."""
        # Set up the mock to raise an exception
        mock_rmtree.side_effect = Exception("Test exception")
        
        # Add a directory that will trigger the exception
        self.cleanup_manager.add_temp_dir(self.test_dir)
        
        # Run cleanup (should not raise an exception)
        self.cleanup_manager.run()
        
        # Verify the rmtree method was called
        mock_rmtree.assert_called_once_with(self.test_dir, ignore_errors=True)

    @patch('windows_dev_toolkit.utils.cleanup.winreg')
    def test_registry_backup_restore(self, mock_winreg):
        """Test registry backup and restore."""
        # Create a mock registry key
        mock_key = MagicMock()
        mock_winreg.CreateKey.return_value.__enter__.return_value = mock_key
        
        # Create mock registry mapping
        mock_winreg.HKEY_LOCAL_MACHINE = 1
        mock_winreg.HKEY_CURRENT_USER = 2
        mock_winreg.REG_DWORD = 3
        
        # Add a registry backup
        test_key = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Test"
        test_data = {
            "TestValue": (3, 1)  # (value_type, value_data)
        }
        self.cleanup_manager.add_registry_backup(test_key, test_data)
        
        # Verify the backup was added
        self.assertIn(test_key, self.cleanup_manager.registry_backups)
        
        # Restore the backup
        self.cleanup_manager.restore_registry_backups()
        
        # Verify the CreateKey was called
        mock_winreg.CreateKey.assert_called_once_with(1, "SOFTWARE\\Test")
        
        # Verify SetValueEx was called
        mock_winreg.SetValueEx.assert_called_once_with(
            mock_key, "TestValue", 0, 3, 1
        )
        
        # Verify the registry backups were cleared
        self.assertEqual(len(self.cleanup_manager.registry_backups), 0)


if __name__ == '__main__':
    unittest.main()