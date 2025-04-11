"""
TUI Manager Module

This module handles the text-based user interface for the Windows Developer Utilities Toolkit.
"""
import os
import sys
import time
from typing import List, Any, Optional, Callable

class TUIManager:
    """
    Text-based User Interface manager for the Windows Developer Utilities Toolkit.
    Provides consistent UI elements and interaction patterns.
    """
    
    # ANSI color codes
    COLORS = {
        "RESET": "\033[0m",
        "BLACK": "\033[30m",
        "RED": "\033[31m",
        "GREEN": "\033[32m",
        "YELLOW": "\033[33m",
        "BLUE": "\033[34m",
        "MAGENTA": "\033[35m",
        "CYAN": "\033[36m",
        "WHITE": "\033[37m",
        "BOLD": "\033[1m",
        "UNDERLINE": "\033[4m",
        "BG_BLACK": "\033[40m",
        "BG_RED": "\033[41m",
        "BG_GREEN": "\033[42m",
        "BG_YELLOW": "\033[43m",
        "BG_BLUE": "\033[44m",
        "BG_MAGENTA": "\033[45m",
        "BG_CYAN": "\033[46m",
        "BG_WHITE": "\033[47m",
    }
    
    def __init__(self):
        """Initialize the TUI manager"""
        self._setup_console()
        self.width = 80  # Default width
        
    def _setup_console(self):
        """Set up the console for ANSI colors"""
        # Enable ANSI colors on Windows
        if os.name == 'nt':
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            
    def _clear_screen(self):
        """Clear the console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def _print_header(self, title: str):
        """Print a styled header"""
        print(f"\n{self.COLORS['BOLD']}{self.COLORS['CYAN']}{'=' * self.width}{self.COLORS['RESET']}")
        print(f"{self.COLORS['BOLD']}{self.COLORS['CYAN']}{title.center(self.width)}{self.COLORS['RESET']}")
        print(f"{self.COLORS['BOLD']}{self.COLORS['CYAN']}{'=' * self.width}{self.COLORS['RESET']}\n")
        
    def _print_footer(self):
        """Print a styled footer"""
        print(f"\n{self.COLORS['BOLD']}{self.COLORS['CYAN']}{'=' * self.width}{self.COLORS['RESET']}\n")
        
    def display_welcome(self):
        """Display welcome screen"""
        self._clear_screen()
        
        welcome_text = [
            f"{self.COLORS['BOLD']}{self.COLORS['GREEN']}Windows Developer Utilities Toolkit{self.COLORS['RESET']}",
            f"{self.COLORS['CYAN']}A comprehensive utility suite for Windows developers{self.COLORS['RESET']}",
            "",
            f"{self.COLORS['YELLOW']}Version: 1.0.0{self.COLORS['RESET']}",
            f"{self.COLORS['YELLOW']}Copyright (c) 2025 - Your Development Team{self.COLORS['RESET']}",
            "",
            f"{self.COLORS['RED']}IMPORTANT: This toolkit requires administrator privileges{self.COLORS['RESET']}",
            f"{self.COLORS['RED']}It should only be used for legitimate development purposes{self.COLORS['RESET']}",
        ]
        
        print("\n" * 2)
        for line in welcome_text:
            print(line.center(self.width))
        print("\n" * 2)
        
        input(f"{self.COLORS['GREEN']}Press Enter to continue...{self.COLORS['RESET']}")
        
    def display_goodbye(self):
        """Display goodbye message"""
        self._clear_screen()
        
        goodbye_text = [
            f"{self.COLORS['BOLD']}{self.COLORS['GREEN']}Thank you for using Windows Developer Utilities Toolkit{self.COLORS['RESET']}",
            "",
            f"{self.COLORS['CYAN']}All operations completed{self.COLORS['RESET']}",
            f"{self.COLORS['CYAN']}Temporary files have been cleaned up{self.COLORS['RESET']}",
            "",
            f"{self.COLORS['YELLOW']}Have a productive day!{self.COLORS['RESET']}",
        ]
        
        print("\n" * 2)
        for line in goodbye_text:
            print(line.center(self.width))
        print("\n" * 2)
        
    def display_main_menu(self) -> str:
        """Display main menu and get user choice"""
        options = [
            ("environment", "Development Environment Setup"),
            ("office", "Office LTSC Management"),
            ("windows", "Windows Configuration"),
            ("exit", "Exit")
        ]
        
        self._clear_screen()
        self._print_header("MAIN MENU")
        
        for i, (key, label) in enumerate(options):
            print(f"{self.COLORS['BOLD']}{self.COLORS['YELLOW']}[{i+1}]{self.COLORS['RESET']} {label}")
            
        self._print_footer()
        
        while True:
            try:
                choice = input(f"{self.COLORS['GREEN']}Enter your choice (1-{len(options)}): {self.COLORS['RESET']}")
                choice_idx = int(choice) - 1
                
                if 0 <= choice_idx < len(options):
                    return options[choice_idx][0]
                    
                print(f"{self.COLORS['RED']}Invalid choice. Please try again.{self.COLORS['RESET']}")
                
            except ValueError:
                print(f"{self.COLORS['RED']}Please enter a number.{self.COLORS['RESET']}")
                
    def display_menu(self, title: str, options: List[str]) -> int:
        """Display a menu with options and return the selected index"""
        self._clear_screen()
        self._print_header(title)
        
        for i, option in enumerate(options):
            print(f"{self.COLORS['BOLD']}{self.COLORS['YELLOW']}[{i+1}]{self.COLORS['RESET']} {option}")
            
        self._print_footer()
        
        while True:
            try:
                choice = input(f"{self.COLORS['GREEN']}Enter your choice (1-{len(options)}): {self.COLORS['RESET']}")
                choice_idx = int(choice) - 1
                
                if 0 <= choice_idx < len(options):
                    return choice_idx
                    
                print(f"{self.COLORS['RED']}Invalid choice. Please try again.{self.COLORS['RESET']}")
                
            except ValueError:
                print(f"{self.COLORS['RED']}Please enter a number.{self.COLORS['RESET']}")
                
    def display_info(self, message: str):
        """Display an informational message"""
        print(f"{self.COLORS['CYAN']}[INFO] {message}{self.COLORS['RESET']}")
        
    def display_success(self, message: str):
        """Display a success message"""
        print(f"{self.COLORS['GREEN']}[SUCCESS] {message}{self.COLORS['RESET']}")
        
    def display_warning(self, message: str):
        """Display a warning message"""
        print(f"{self.COLORS['YELLOW']}[WARNING] {message}{self.COLORS['RESET']}")
        
    def display_error(self, message: str):
        """Display an error message"""
        print(f"{self.COLORS['RED']}[ERROR] {message}{self.COLORS['RESET']}")
        
    def display_progress(self, message: str):
        """Display a progress message"""
        print(f"{self.COLORS['MAGENTA']}[PROGRESS] {message}{self.COLORS['RESET']}")
        
    def update_progress(self, percentage: float):
        """Update a progress bar"""
        bar_length = 50
        filled_length = int(bar_length * percentage / 100)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        print(f"\r{self.COLORS['MAGENTA']}Progress: |{bar}| {percentage:.1f}%{self.COLORS['RESET']}", end='')
        if percentage >= 100:
            print()
            
    def confirm(self, message: str) -> bool:
        """Ask for user confirmation"""
        response = input(f"{self.COLORS['YELLOW']}[CONFIRM] {message} (y/n): {self.COLORS['RESET']}")
        return response.lower().startswith('y')
        
    def prompt_input(self, message: str, default: str = "") -> str:
        """Prompt user for text input"""
        if default:
            prompt = f"{self.COLORS['GREEN']}[INPUT] {message} [{default}]: {self.COLORS['RESET']}"
        else:
            prompt = f"{self.COLORS['GREEN']}[INPUT] {message}: {self.COLORS['RESET']}"
            
        response = input(prompt)
        return response if response else default
        
    def prompt_choice(self, message: str, options: List[str]) -> int:
        """Prompt user to choose from a list of options"""
        print(f"{self.COLORS['GREEN']}[CHOICE] {message}{self.COLORS['RESET']}")
        
        for i, option in enumerate(options):
            print(f"{self.COLORS['YELLOW']}    [{i+1}] {option}{self.COLORS['RESET']}")
            
        while True:
            try:
                choice = input(f"{self.COLORS['GREEN']}Enter choice (1-{len(options)}): {self.COLORS['RESET']}")
                choice_idx = int(choice) - 1
                
                if 0 <= choice_idx < len(options):
                    return choice_idx
                    
                print(f"{self.COLORS['RED']}Invalid choice. Please try again.{self.COLORS['RESET']}")
                
            except ValueError:
                print(f"{self.COLORS['RED']}Please enter a number.{self.COLORS['RESET']}")
                
    def prompt_multichoice(self, message: str, options: List[str]) -> List[int]:
        """Prompt user to choose multiple options from a list"""
        print(f"{self.COLORS['GREEN']}[MULTI-CHOICE] {message}{self.COLORS['RESET']}")
        print(f"{self.COLORS['CYAN']}(Enter comma-separated numbers, e.g., 1,3,4){self.COLORS['RESET']}")
        
        for i, option in enumerate(options):
            print(f"{self.COLORS['YELLOW']}    [{i+1}] {option}{self.COLORS['RESET']}")
            
        while True:
            try:
                choices = input(f"{self.COLORS['GREEN']}Enter choices (1-{len(options)}): {self.COLORS['RESET']}")
                
                if not choices.strip():
                    return []
                    
                choice_indices = [int(x.strip()) - 1 for x in choices.split(',')]
                
                if all(0 <= idx < len(options) for idx in choice_indices):
                    return choice_indices
                    
                print(f"{self.COLORS['RED']}Invalid choices. Please try again.{self.COLORS['RESET']}")
                
            except ValueError:
                print(f"{self.COLORS['RED']}Please enter comma-separated numbers.{self.COLORS['RESET']}")