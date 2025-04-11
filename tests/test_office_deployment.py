"""
Tests for the Office LTSC Management module.
"""
import unittest
from unittest.mock import patch, MagicMock, call
import sys
import os
import tempfile
import xml.etree.ElementTree as ET

# Add local path to import modules
sys.path.append('.')

from windows_dev_toolkit.modules.office_deployment import OfficeLTSCManager


class TestOfficeLTSCManager(unittest.TestCase):
    """Test cases for Office LTSC Management functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock config
        self.config = {
            "office": {
                "download_path": tempfile.mkdtemp(),
                "odt_url": "https://example.com/odt.exe"
            }
        }
        
        # Create the manager instance
        self.office_manager = OfficeLTSCManager(self.config)
        
        # Create a mock UI
        self.mock_ui = MagicMock()

    def tearDown(self):
        """Tear down test fixtures."""
        # Clean up temporary files
        if hasattr(self, 'temp_dir') and self.temp_dir and os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)

    @patch('requests.get')
    @patch('subprocess.run')
    def test_download_odt(self, mock_run, mock_get):
        """Test downloading the Office Deployment Tool."""
        # Set up mock response
        mock_response = MagicMock()
        mock_response.headers.get.return_value = '1000'
        mock_response.iter_content.return_value = [b'chunk1', b'chunk2']
        mock_get.return_value = mock_response
        
        # Set up mock subprocess
        mock_run.return_value.returncode = 0
        
        # Call the download method
        self.office_manager._download_odt(self.mock_ui)
        
        # Verify requests.get was called with the correct URL
        mock_get.assert_called_once()
        
        # Verify subprocess.run was called to extract
        mock_run.assert_called_once()
        
        # Verify UI methods were called
        self.mock_ui.display_info.assert_called()
        self.mock_ui.display_progress.assert_called_once()
        self.mock_ui.update_progress.assert_called()
        self.mock_ui.display_success.assert_called_once()
        
        # Verify temp_dir and odt_path were set
        self.assertIsNotNone(self.office_manager.temp_dir)
        self.assertIsNotNone(self.office_manager.odt_path)

    def test_generate_config_xml(self):
        """Test generation of Office configuration XML."""
        # Set up test configuration
        config = {
            "architecture": 1,  # 64-bit
            "language": "en-us",
            "products": [0, 2]  # ProPlus and Visio
        }
        
        # Generate the XML
        xml_content = self.office_manager._generate_config_xml(config)
        
        # Verify the XML structure
        self.assertIn('<?xml version="1.0" encoding="UTF-8"?>', xml_content)
        
        # Parse the XML for further verification
        root = ET.fromstring(xml_content.replace('<?xml version="1.0" encoding="UTF-8"?>\n', ''))
        
        # Check root element
        self.assertEqual(root.tag, "Configuration")
        
        # Check Add element attributes
        add = root.find("Add")
        self.assertIsNotNone(add)
        self.assertEqual(add.get("OfficeClientEdition"), "64")
        self.assertEqual(add.get("Channel"), "PerpetualVL2021")
        
        # Check Product elements
        products = add.findall("Product")
        self.assertEqual(len(products), 2)
        
        # Check first product (ProPlus)
        self.assertEqual(products[0].get("ID"), "ProPlus2021Volume")
        
        # Check second product (Visio)
        self.assertEqual(products[1].get("ID"), "VisioPro2021Volume")
        
        # Check language
        for product in products:
            language = product.find("Language")
            self.assertIsNotNone(language)
            self.assertEqual(language.get("ID"), "en-us")

    @patch('os.path.exists')
    @patch('subprocess.run')
    def test_deploy_office(self, mock_run, mock_exists):
        """Test deploying Office LTSC."""
        # Set up mocks
        mock_exists.return_value = True
        mock_run.return_value.returncode = 0
        
        # Set up manager with odt_path
        self.office_manager.odt_path = "/mock/odt/path"
        
        # Set up UI for confirmation
        self.mock_ui.confirm.side_effect = [True, True]
        
        # Call the deploy method
        self.office_manager._deploy_office(self.mock_ui)
        
        # Verify confirmation was asked
        self.assertEqual(self.mock_ui.confirm.call_count, 2)
        
        # Verify subprocess.run was called to run setup.exe
        mock_run.assert_called_once()
        
        # Verify UI methods were called
        self.mock_ui.display_info.assert_called()
        self.mock_ui.display_success.assert_called_once()

    @patch('os.path.exists')
    def test_check_odt(self, mock_exists):
        """Test ODT availability check."""
        # Test when ODT is not available
        self.office_manager.odt_path = None
        mock_exists.return_value = False
        
        # Call the check method
        result = self.office_manager._check_odt(self.mock_ui)
        
        # Verify result is False
        self.assertFalse(result)
        
        # Verify error message was displayed
        self.mock_ui.display_error.assert_called_once()
        
        # Reset mock
        self.mock_ui.reset_mock()
        
        # Test when ODT is available
        self.office_manager.odt_path = "/mock/odt/path"
        mock_exists.return_value = True
        
        # Call the check method
        result = self.office_manager._check_odt(self.mock_ui)
        
        # Verify result is True
        self.assertTrue(result)
        
        # Verify no error message was displayed
        self.mock_ui.display_error.assert_not_called()

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    @patch('subprocess.run')
    def test_remove_office(self, mock_run, mock_open, mock_exists):
        """Test removing Office installations."""
        # Set up mocks
        mock_exists.return_value = True
        mock_run.return_value.returncode = 0
        
        # Set up manager with odt_path
        self.office_manager.odt_path = "/mock/odt/path"
        
        # Set up UI for confirmation
        self.mock_ui.confirm.return_value = True
        
        # Call the remove method
        self.office_manager._remove_office(self.mock_ui)
        
        # Verify confirmation was asked
        self.mock_ui.confirm.assert_called_once()
        
        # Verify file was opened to write the removal config
        mock_open.assert_called_once()
        
        # Verify subprocess.run was called to run setup.exe
        mock_run.assert_called_once()
        
        # Verify UI methods were called
        self.mock_ui.display_info.assert_called()
        self.mock_ui.display_success.assert_called_once()


if __name__ == '__main__':
    unittest.main()