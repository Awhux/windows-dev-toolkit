"""
Admin Privileges Check Utility

This module provides functionality to verify if the application
is running with administrator privileges.
"""
import os
import sys
import logging

def verify_admin_privileges():
    """
    Check if the script is running with administrator privileges.
    
    Returns:
        bool: True if running as administrator, False otherwise
    """
    logger = logging.getLogger("admin_check")
    
    if os.name == 'nt':  # Windows
        try:
            import ctypes
            result = ctypes.windll.shell32.IsUserAnAdmin() != 0
            
            if result:
                logger.info("Application is running with administrator privileges")
            else:
                logger.warning("Application is NOT running with administrator privileges")
                
            return result
        except Exception as e:
            logger.error(f"Error checking admin privileges: {str(e)}")
            return False
    else:  # Non-Windows (not supported)
        logger.warning("Admin check not supported on non-Windows platforms")
        return False