"""
Integration tests for the Windows Developer Utilities Toolkit.
"""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import tempfile

# Add local path to import modules
sys.path.append('.')

# Import main module to test
from windows_dev_toolkit.main import DeveloperToolkit


class TestIntegration(unittest.TestCase):
    """Integration test cases for the Windows Developer Utilities Toolkit."""

    @patch('windows_dev_toolkit.utils.admin_check.verify_admin_privileges')
    def setUp(self, mock_admin_check):
        """Set up test fixtures."""
        # Mock admin check to return True
        mock_admin_check.return_value = True
        
        # Create a temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        
        # Create toolkit instance
        self.toolkit = DeveloperToolkit()
        
        # Mock TUI
        self.toolkit.tui = MagicMock()

    def tearDown(self):
        """Tear down test fixtures."""
        # Clean up temporary directory
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)

    @patch('windows_dev_toolkit.utils.admin_check.verify_admin_privileges')
    def test_toolkit_init(self, mock_admin_check):
        """Test toolkit initialization."""
        # Mock admin check to return True
        mock_admin_check.return_value = True
        
        # Create toolkit instance
        toolkit = DeveloperToolkit()
        
        # Verify logger was set up
        self.assertIsNotNone(toolkit.logger)
        
        # Verify config was loaded
        self.assertIsNotNone(toolkit.config)
        
        # Verify TUI was initialized
        self.assertIsNotNone(toolkit.tui)
        
        # Verify cleanup manager was initialized
        self.assertIsNotNone(toolkit.cleanup)
        
        # Verify modules were registered
        self.assertIn("environment", toolkit.modules)
        self.assertIn("office", toolkit.modules)
        self.assertIn("windows", toolkit.modules)

    @patch('windows_dev_toolkit.utils.admin_check.verify_admin_privileges')
    def test_toolkit_run_no_admin(self, mock_admin_check):
        """Test toolkit run without admin privileges."""
        # Mock admin check to return False
        mock_admin_check.return_value = False
        
        # Create toolkit instance with mocked components
        toolkit = DeveloperToolkit()
        toolkit.tui = MagicMock()
        
        # Run the toolkit with mocked sys.exit
        with patch('sys.exit') as mock_exit:
            toolkit.run()
            
            # Verify error message was displayed
            toolkit.tui.display_error.assert_called_once()
            
            # Verify sys.exit was called
            mock_exit.assert_called_once_with(1)

    @patch('windows_dev_toolkit.utils.admin_check.verify_admin_privileges')
    def test_toolkit_run_with_admin(self, mock_admin_check):
        """Test toolkit run with admin privileges."""
        # Mock admin check to return True
        mock_admin_check.return_value = True
        
        # Create toolkit instance with mocked components
        toolkit = DeveloperToolkit()
        toolkit.tui = MagicMock()
        
        # Setup menu navigation: show welcome -> select exit
        toolkit.tui.display_main_menu.return_value = "exit"
        
        # Run the toolkit
        toolkit.run()
        
        # Verify welcome was displayed
        toolkit.tui.display_welcome.assert_called_once()
        
        # Verify main menu was displayed
        toolkit.tui.display_main_menu.assert_called_once()
        
        # Verify goodbye was displayed
        toolkit.tui.display_goodbye.assert_called_once()

    @patch('windows_dev_toolkit.utils.admin_check.verify_admin_privileges')
    def test_toolkit_module_selection(self, mock_admin_check):
        """Test toolkit module selection and execution."""
        # Mock admin check to return True
        mock_admin_check.return_value = True
        
        # Create toolkit instance with mocked components
        toolkit = DeveloperToolkit()
        toolkit.tui = MagicMock()
        
        # Mock modules
        toolkit.modules = {
            "environment": MagicMock(),
            "office": MagicMock(),
            "windows": MagicMock()
        }
        
        # Setup menu navigation: select environment -> then exit
        toolkit.tui.display_main_menu.side_effect = ["environment", "exit"]
        
        # Run the toolkit
        toolkit.run()
        
        # Verify main menu was displayed twice
        self.assertEqual(toolkit.tui.display_main_menu.call_count, 2)
        
        # Verify environment module was executed
        toolkit.modules["environment"].execute.assert_called_once_with(toolkit.tui)
        
        # Verify other modules were not executed
        toolkit.modules["office"].execute.assert_not_called()
        toolkit.modules["windows"].execute.assert_not_called()

    @patch('windows_dev_toolkit.utils.admin_check.verify_admin_privileges')
    def test_toolkit_exception_handling(self, mock_admin_check):
        """Test toolkit exception handling."""
        # Mock admin check to return True
        mock_admin_check.return_value = True
        
        # Create toolkit instance with mocked components
        toolkit = DeveloperToolkit()
        toolkit.tui = MagicMock()
        toolkit.logger = MagicMock()
        
        # Setup main menu to raise an exception
        test_exception = Exception("Test exception")
        toolkit.tui.display_main_menu.side_effect = test_exception
        
        # Run the toolkit
        toolkit.run()
        
        # Verify welcome was displayed
        toolkit.tui.display_welcome.assert_called_once()
        
        # Verify error was logged
        toolkit.logger.error.assert_called_once()
        
        # Verify error was displayed
        toolkit.tui.display_error.assert_called_once()
        
        # Verify goodbye was displayed (cleanup still runs)
        toolkit.tui.display_goodbye.assert_called_once()

    @patch('windows_dev_toolkit.utils.admin_check.verify_admin_privileges')
    def test_toolkit_cleanup(self, mock_admin_check):
        """Test toolkit cleanup on exit."""
        # Mock admin check to return True
        mock_admin_check.return_value = True
        
        # Create toolkit instance with mocked components
        toolkit = DeveloperToolkit()
        toolkit.tui = MagicMock()
        toolkit.cleanup = MagicMock()
        
        # Setup menu navigation: show welcome -> select exit
        toolkit.tui.display_main_menu.return_value = "exit"
        
        # Run the toolkit
        toolkit.run()
        
        # Verify cleanup was run
        toolkit.cleanup.run.assert_called_once()


if __name__ == '__main__':
    unittest.main()