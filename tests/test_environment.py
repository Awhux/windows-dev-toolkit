"""
Tests for the Development Environment Manager module.
"""
import unittest
from unittest.mock import patch, MagicMock, call
import sys
import os
import shutil

# Add local path to import modules
sys.path.append('.')

from windows_dev_toolkit.utils.utility_modules import EnvironmentManager


class TestEnvironmentManager(unittest.TestCase):
    """Test cases for Development Environment Manager functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock config
        self.config = {
            "environment": {
                "python": {
                    "version": "3.10.0",
                    "packages": ["pytest", "black"]
                },
                "nodejs": {
                    "version": "16.13.0",
                    "packages": ["typescript", "eslint"]
                },
                "dotnet": {
                    "version": "6.0",
                    "tools": ["dotnet-ef"]
                }
            }
        }
        
        # Create the manager instance
        self.env_manager = EnvironmentManager(self.config)
        
        # Create a mock UI
        self.mock_ui = MagicMock()

    @patch('subprocess.run')
    @patch('time.sleep')  # Mock sleep to speed up tests
    def test_install_tool(self, mock_sleep, mock_run):
        """Test installing a development tool."""
        # Set up mock subprocess
        mock_run.return_value.returncode = 0
        
        # Test installing git
        self.env_manager._install_tool(self.mock_ui, "git")
        
        # Verify UI methods were called
        self.mock_ui.display_info.assert_called()
        self.mock_ui.update_progress.assert_called()
        self.mock_ui.display_success.assert_called_once_with("Successfully installed git")

    @patch('shutil.which')
    def test_configure_python_not_installed(self, mock_which):
        """Test configuring Python when not installed."""
        # Set up mock to indicate Python is not installed
        mock_which.return_value = None
        
        # Set up UI for prompt
        self.mock_ui.confirm.return_value = False
        
        # Call the configure Python method
        self.env_manager._configure_python(self.mock_ui)
        
        # Verify error message was displayed
        self.mock_ui.display_error.assert_called_once()
        
        # Verify confirmation was asked
        self.mock_ui.confirm.assert_called_once()

    @patch('shutil.which')
    @patch('os.path.exists')
    def test_configure_python_installed(self, mock_exists, mock_which):
        """Test configuring Python when installed."""
        # Set up mock to indicate Python is installed
        mock_which.return_value = "/usr/bin/python"
        
        # Set up mock to indicate venv doesn't exist
        mock_exists.return_value = False
        
        # Set up UI for prompts
        self.mock_ui.prompt_input.return_value = "venv"
        self.mock_ui.confirm.return_value = True
        self.mock_ui.prompt_multichoice.return_value = [0, 1]  # Select packages 0 and 1
        
        # Call the configure Python method
        self.env_manager._configure_python(self.mock_ui)
        
        # Verify Python path was displayed
        self.mock_ui.display_info.assert_any_call("Found Python at: /usr/bin/python")
        
        # Verify venv command was displayed
        self.mock_ui.display_info.assert_any_call("Would run: python -m venv venv")
        
        # Verify package installation command was displayed
        package_info_calls = [
            call for call in self.mock_ui.display_info.call_args_list 
            if "Would run: pip install" in call[0][0]
        ]
        self.assertGreaterEqual(len(package_info_calls), 1)
        
        # Verify success message was displayed
        self.mock_ui.display_success.assert_called_once()

    @patch('shutil.which')
    def test_configure_nodejs_not_installed(self, mock_which):
        """Test configuring Node.js when not installed."""
        # Set up mock to indicate Node.js is not installed
        mock_which.side_effect = lambda cmd: None
        
        # Set up UI for prompt
        self.mock_ui.confirm.return_value = False
        
        # Call the configure Node.js method
        self.env_manager._configure_nodejs(self.mock_ui)
        
        # Verify error message was displayed
        self.mock_ui.display_error.assert_called_once()
        
        # Verify confirmation was asked
        self.mock_ui.confirm.assert_called_once()

    @patch('shutil.which')
    @patch('os.path.exists')
    @patch('os.getcwd')
    def test_configure_nodejs_installed(self, mock_getcwd, mock_exists, mock_which):
        """Test configuring Node.js when installed."""
        # Set up mock to indicate Node.js is installed
        mock_which.side_effect = lambda cmd: "/usr/bin/" + cmd if cmd in ["node", "npm"] else None
        
        # Set up mock for current directory
        mock_getcwd.return_value = "/test/dir"
        
        # Set up mock to indicate package.json doesn't exist
        mock_exists.return_value = False
        
        # Set up UI for prompts
        self.mock_ui.confirm.side_effect = [True, True]  # Yes to init, yes to packages
        self.mock_ui.prompt_input.return_value = "/test/dir"
        self.mock_ui.prompt_multichoice.return_value = [0, 1]  # Select packages 0 and 1
        
        # Call the configure Node.js method
        self.env_manager._configure_nodejs(self.mock_ui)
        
        # Verify Node.js path was displayed
        self.mock_ui.display_info.assert_any_call("Found Node.js at: /usr/bin/node")
        
        # Verify npm path was displayed
        self.mock_ui.display_info.assert_any_call("Found NPM at: /usr/bin/npm")
        
        # Verify npm init command was displayed
        self.mock_ui.display_info.assert_any_call("Would run: npm init -y in /test/dir")
        
        # Verify package installation command was displayed
        package_info_calls = [
            call for call in self.mock_ui.display_info.call_args_list 
            if "Would run: npm install -g" in call[0][0]
        ]
        self.assertGreaterEqual(len(package_info_calls), 1)
        
        # Verify success message was displayed
        self.mock_ui.display_success.assert_called_once()

    @patch('shutil.which')
    def test_configure_dotnet_not_installed(self, mock_which):
        """Test configuring .NET when not installed."""
        # Set up mock to indicate .NET is not installed
        mock_which.return_value = None
        
        # Set up UI for prompt
        self.mock_ui.confirm.return_value = False
        
        # Call the configure .NET method
        self.env_manager._configure_dotnet(self.mock_ui)
        
        # Verify error message was displayed
        self.mock_ui.display_error.assert_called_once()
        
        # Verify confirmation was asked
        self.mock_ui.confirm.assert_called_once()

    @patch('shutil.which')
    @patch('os.path.exists')
    @patch('os.path.join')
    def test_configure_dotnet_installed(self, mock_join, mock_exists, mock_which):
        """Test configuring .NET when installed."""
        # Set up mock to indicate .NET is installed
        mock_which.return_value = "/usr/bin/dotnet"
        
        # Set up mock for path joining
        mock_join.return_value = "/test/dir/MyDotNetApp"
        
        # Set up mock to indicate project path doesn't exist
        mock_exists.return_value = False
        
        # Set up UI for prompts
        self.mock_ui.confirm.side_effect = [True, True]  # Yes to create project, yes to tools
        self.mock_ui.prompt_choice.return_value = 0  # Select console
        self.mock_ui.prompt_input.side_effect = ["MyDotNetApp", "/test/dir"]
        self.mock_ui.prompt_multichoice.return_value = [0]  # Select tool 0
        
        # Call the configure .NET method
        self.env_manager._configure_dotnet(self.mock_ui)
        
        # Verify .NET path was displayed
        self.mock_ui.display_info.assert_any_call("Found .NET at: /usr/bin/dotnet")
        
        # Verify project creation command was displayed
        project_info_calls = [
            call for call in self.mock_ui.display_info.call_args_list 
            if "Would run: dotnet new" in call[0][0]
        ]
        self.assertGreaterEqual(len(project_info_calls), 1)
        
        # Verify tool installation command was displayed
        tool_info_calls = [
            call for call in self.mock_ui.display_info.call_args_list 
            if "Would run: dotnet tool install" in call[0][0]
        ]
        self.assertGreaterEqual(len(tool_info_calls), 1)
        
        # Verify success message was displayed
        self.mock_ui.display_success.assert_called_once()


if __name__ == '__main__':
    unittest.main()