"""
Tests for the TUI (Text User Interface) manager module.
"""
import unittest
from unittest.mock import patch, MagicMock
import sys
import io

# Add local path to import modules
sys.path.append('.')

from windows_dev_toolkit.utils.ui import TUIManager


class TestTUIManager(unittest.TestCase):
    """Test cases for TUI manager functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.tui = TUIManager()
        
        # Patch stdout to capture output
        self.stdout_patcher = patch('sys.stdout', new_callable=io.StringIO)
        self.mock_stdout = self.stdout_patcher.start()

    def tearDown(self):
        """Tear down test fixtures."""
        self.stdout_patcher.stop()

    @patch('os.system')
    def test_clear_screen(self, mock_system):
        """Test clear screen functionality."""
        # Call the clear screen method
        self.tui._clear_screen()
        
        # Verify os.system was called with the correct command
        if sys.platform == 'win32':
            mock_system.assert_called_once_with('cls')
        else:
            mock_system.assert_called_once_with('clear')

    def test_print_header(self):
        """Test header printing."""
        # Call the header method
        self.tui._print_header("Test Header")
        
        # Get the output
        output = self.mock_stdout.getvalue()
        
        # Verify the header contains the title
        self.assertIn("Test Header", output)
        
        # Verify there are separator lines
        self.assertIn("=", output)

    def test_display_info(self):
        """Test displaying info messages."""
        # Display an info message
        self.tui.display_info("Test info message")
        
        # Get the output
        output = self.mock_stdout.getvalue()
        
        # Verify the message is in the output
        self.assertIn("Test info message", output)
        
        # Verify the INFO prefix is present
        self.assertIn("[INFO]", output)

    def test_display_error(self):
        """Test displaying error messages."""
        # Display an error message
        self.tui.display_error("Test error message")
        
        # Get the output
        output = self.mock_stdout.getvalue()
        
        # Verify the message is in the output
        self.assertIn("Test error message", output)
        
        # Verify the ERROR prefix is present
        self.assertIn("[ERROR]", output)

    def test_display_success(self):
        """Test displaying success messages."""
        # Display a success message
        self.tui.display_success("Test success message")
        
        # Get the output
        output = self.mock_stdout.getvalue()
        
        # Verify the message is in the output
        self.assertIn("Test success message", output)
        
        # Verify the SUCCESS prefix is present
        self.assertIn("[SUCCESS]", output)

    def test_display_warning(self):
        """Test displaying warning messages."""
        # Display a warning message
        self.tui.display_warning("Test warning message")
        
        # Get the output
        output = self.mock_stdout.getvalue()
        
        # Verify the message is in the output
        self.assertIn("Test warning message", output)
        
        # Verify the WARNING prefix is present
        self.assertIn("[WARNING]", output)

    @patch('builtins.input', return_value='y')
    def test_confirm_yes(self, mock_input):
        """Test confirmation dialog with 'yes' response."""
        # Call confirm method
        result = self.tui.confirm("Test confirmation?")
        
        # Verify input was called with the right message
        mock_input.assert_called_once()
        self.assertIn("Test confirmation?", mock_input.call_args[0][0])
        
        # Verify result is True (yes)
        self.assertTrue(result)

    @patch('builtins.input', return_value='n')
    def test_confirm_no(self, mock_input):
        """Test confirmation dialog with 'no' response."""
        # Call confirm method
        result = self.tui.confirm("Test confirmation?")
        
        # Verify input was called with the right message
        mock_input.assert_called_once()
        self.assertIn("Test confirmation?", mock_input.call_args[0][0])
        
        # Verify result is False (no)
        self.assertFalse(result)

    @patch('builtins.input', return_value='test input')
    def test_prompt_input(self, mock_input):
        """Test input prompt."""
        # Call prompt_input method
        result = self.tui.prompt_input("Enter test:")
        
        # Verify input was called with the right message
        mock_input.assert_called_once()
        self.assertIn("Enter test:", mock_input.call_args[0][0])
        
        # Verify result matches the input
        self.assertEqual(result, "test input")

    @patch('builtins.input', return_value='')
    def test_prompt_input_default(self, mock_input):
        """Test input prompt with default value."""
        # Call prompt_input method with a default
        result = self.tui.prompt_input("Enter test:", default="default value")
        
        # Verify input was called with the right message including default
        mock_input.assert_called_once()
        input_prompt = mock_input.call_args[0][0]
        self.assertIn("Enter test:", input_prompt)
        self.assertIn("default value", input_prompt)
        
        # Verify result matches the default
        self.assertEqual(result, "default value")

    @patch('builtins.input', side_effect=['2'])
    def test_prompt_choice(self, mock_input):
        """Test choice prompt."""
        # Define options
        options = ["Option 1", "Option 2", "Option 3"]
        
        # Call prompt_choice method
        result = self.tui.prompt_choice("Select option:", options)
        
        # Verify input was called
        mock_input.assert_called_once()
        
        # Verify result matches the expected index (2-1=1)
        self.assertEqual(result, 1)

    @patch('builtins.input', side_effect=['invalid', '4', '2'])
    def test_prompt_choice_validation(self, mock_input):
        """Test choice prompt with validation."""
        # Define options
        options = ["Option 1", "Option 2", "Option 3"]
        
        # Call prompt_choice method
        result = self.tui.prompt_choice("Select option:", options)
        
        # Verify input was called multiple times due to validation
        self.assertEqual(mock_input.call_count, 3)
        
        # Verify result matches the expected index (2-1=1)
        self.assertEqual(result, 1)

    @patch('builtins.input', side_effect=['1,3'])
    def test_prompt_multichoice(self, mock_input):
        """Test multi-choice prompt."""
        # Define options
        options = ["Option 1", "Option 2", "Option 3", "Option 4"]
        
        # Call prompt_multichoice method
        result = self.tui.prompt_multichoice("Select options:", options)
        
        # Verify input was called
        mock_input.assert_called_once()
        
        # Verify result matches the expected indices (1-1=0, 3-1=2)
        self.assertEqual(result, [0, 2])

    @patch('builtins.input', side_effect=[''])
    def test_prompt_multichoice_empty(self, mock_input):
        """Test multi-choice prompt with empty input."""
        # Define options
        options = ["Option 1", "Option 2", "Option 3"]
        
        # Call prompt_multichoice method
        result = self.tui.prompt_multichoice("Select options:", options)
        
        # Verify input was called
        mock_input.assert_called_once()
        
        # Verify result is an empty list
        self.assertEqual(result, [])


if __name__ == '__main__':
    unittest.main()