"""
Environment Setup Module

This module handles development environment setup for various technologies.
"""
import os
import sys
import logging
import time
import shutil
from typing import List, Dict, Any, Optional

class EnvironmentManager:
    """
    Manages development environment setup.
    This includes installing essential development tools and configuring environments.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the environment manager"""
        self.config = config
        self.logger = logging.getLogger("environment")
        
    def execute(self, ui):
        """Main execution flow for environment setup"""
        options = [
            "Install Development Tools",
            "Configure Python Environment",
            "Configure Node.js Environment",
            "Configure .NET Environment",
            "Back to main menu"
        ]
        
        while True:
            choice = ui.display_menu("Development Environment Setup", options)
            
            if choice == 4:  # Back to main menu
                break
            elif choice == 0:
                self._install_dev_tools(ui)
            elif choice == 1:
                self._configure_python(ui)
            elif choice == 2:
                self._configure_nodejs(ui)
            elif choice == 3:
                self._configure_dotnet(ui)
    
    def _install_dev_tools(self, ui):
        """Install essential development tools"""
        ui.display_info("Installing development tools...")
        
        # Define available development tools
        tools = [
            ("git", "Git for Windows"),
            ("vscode", "Visual Studio Code"),
            ("visualstudio", "Visual Studio 2022 Community"),
            ("docker", "Docker Desktop"),
            ("wsl", "Windows Subsystem for Linux"),
            ("python", "Python"),
            ("nodejs", "Node.js"),
            ("dotnet", ".NET SDK")
        ]
        
        # Let user select tools to install
        tool_names = [t[1] for t in tools]
        selected_indices = ui.prompt_multichoice("Select tools to install:", tool_names)
        
        if not selected_indices:
            ui.display_info("No tools selected")
            return
            
        # Confirm with user
        selected_tools = [tools[i][0] for i in selected_indices]
        selected_names = [tools[i][1] for i in selected_indices]
        
        ui.display_info("You selected the following tools:")
        for name in selected_names:
            ui.display_info(f"- {name}")
            
        if not ui.confirm("Install these development tools?"):
            ui.display_info("Operation cancelled")
            return
            
        # Install selected tools
        for tool, name in zip(selected_tools, selected_names):
            ui.display_info(f"Installing {name}...")
            
            try:
                self._install_tool(ui, tool)
            except Exception as e:
                ui.display_error(f"Error installing {name}: {str(e)}")
                self.logger.error(f"Tool installation error: {str(e)}")
        
        ui.display_success("Development tools installation completed")
    
    def _install_tool(self, ui, tool_id):
        """Install a specific development tool"""
        # In a real implementation, this would use winget, chocolatey, or direct download
        # For this example, we'll just show the commands that would be used
        
        if tool_id == "git":
            ui.display_info("Would run: winget install --id Git.Git -e --source winget")
            # subprocess.run(["winget", "install", "--id", "Git.Git", "-e", "--source", "winget"])
        elif tool_id == "vscode":
            ui.display_info("Would run: winget install --id Microsoft.VisualStudioCode -e --source winget")
        elif tool_id == "visualstudio":
            ui.display_info("Would run: winget install --id Microsoft.VisualStudio.2022.Community -e --source winget")
        elif tool_id == "docker":
            ui.display_info("Would run: winget install --id Docker.DockerDesktop -e --source winget")
        elif tool_id == "wsl":
            ui.display_info("Would run: wsl --install")
        elif tool_id == "python":
            ui.display_info("Would run: winget install --id Python.Python.3.10 -e --source winget")
        elif tool_id == "nodejs":
            ui.display_info("Would run: winget install --id OpenJS.NodeJS -e --source winget")
        elif tool_id == "dotnet":
            ui.display_info("Would run: winget install --id Microsoft.DotNet.SDK.6 -e --source winget")
        
        # Simulate installation
        import time
        for i in range(5):
            ui.update_progress(i * 20)
            time.sleep(0.2)
        ui.update_progress(100)
        
        ui.display_success(f"Successfully installed {tool_id}")
    
    def _configure_python(self, ui):
        """Configure Python development environment"""
        ui.display_info("Configuring Python environment...")
        
        # Check if Python is installed
        import shutil
        python_path = shutil.which("python") or shutil.which("python3")
        
        if not python_path:
            ui.display_error("Python is not installed or not in PATH")
            if ui.confirm("Would you like to install Python?"):
                self._install_tool(ui, "python")
            else:
                return
        
        # Get Python information
        ui.display_info(f"Found Python at: {python_path}")
        
        # Configure virtual environment
        venv_path = ui.prompt_input("Enter path for virtual environment:", "venv")
        
        if os.path.exists(venv_path):
            if not ui.confirm(f"Virtual environment at {venv_path} already exists. Recreate?"):
                ui.display_info("Using existing virtual environment")
            else:
                # In a real implementation, this would execute the commands
                ui.display_info(f"Would run: python -m venv {venv_path} --clear")
        else:
            ui.display_info(f"Would run: python -m venv {venv_path}")
        
        # Install required packages
        if ui.confirm("Install common development packages?"):
            packages = [
                "pytest", "black", "flake8", "mypy", "isort",
                "sphinx", "pylint", "coverage", "virtualenv"
            ]
            
            selected_packages = ui.prompt_multichoice("Select packages to install:", packages)
            
            if selected_packages:
                selected_names = [packages[i] for i in selected_packages]
                packages_str = " ".join(selected_names)
                ui.display_info(f"Would run: pip install {packages_str}")
        
        ui.display_success("Python environment configured successfully")
    
    def _configure_nodejs(self, ui):
        """Configure Node.js development environment"""
        ui.display_info("Configuring Node.js environment...")
        
        # Check if Node.js is installed
        import shutil
        node_path = shutil.which("node")
        npm_path = shutil.which("npm")
        
        if not node_path or not npm_path:
            ui.display_error("Node.js is not installed or not in PATH")
            if ui.confirm("Would you like to install Node.js?"):
                self._install_tool(ui, "nodejs")
            else:
                return
        
        # Get Node.js information
        ui.display_info(f"Found Node.js at: {node_path}")
        ui.display_info(f"Found NPM at: {npm_path}")
        
        # Initialize a project
        if ui.confirm("Initialize a new Node.js project?"):
            project_path = ui.prompt_input("Enter project path:", os.getcwd())
            
            if os.path.exists(os.path.join(project_path, "package.json")):
                ui.display_warning("Project already initialized (package.json exists)")
            else:
                ui.display_info(f"Would run: npm init -y in {project_path}")
        
        # Install global packages
        if ui.confirm("Install common global packages?"):
            packages = [
                "typescript", "nodemon", "eslint", "prettier", 
                "jest", "ts-node", "yarn", "pm2"
            ]
            
            selected_packages = ui.prompt_multichoice("Select packages to install globally:", packages)
            
            if selected_packages:
                selected_names = [packages[i] for i in selected_packages]
                packages_str = " ".join(selected_names)
                ui.display_info(f"Would run: npm install -g {packages_str}")
        
        ui.display_success("Node.js environment configured successfully")
    
    def _configure_dotnet(self, ui):
        """Configure .NET development environment"""
        ui.display_info("Configuring .NET environment...")
        
        # Check if .NET is installed
        import shutil
        dotnet_path = shutil.which("dotnet")
        
        if not dotnet_path:
            ui.display_error(".NET SDK is not installed or not in PATH")
            if ui.confirm("Would you like to install .NET SDK?"):
                self._install_tool(ui, "dotnet")
            else:
                return
        
        # Get .NET information
        ui.display_info(f"Found .NET at: {dotnet_path}")
        
        # Create a new project
        if ui.confirm("Create a new .NET project?"):
            project_types = [
                "console", "classlib", "wpf", "winforms", 
                "web", "webapi", "mvc", "blazor"
            ]
            
            project_type = project_types[ui.prompt_choice("Select project type:", project_types)]
            project_name = ui.prompt_input("Enter project name:", "MyDotNetApp")
            project_path = ui.prompt_input("Enter project path:", os.getcwd())
            
            full_path = os.path.join(project_path, project_name)
            
            if os.path.exists(full_path):
                ui.display_warning(f"Directory {full_path} already exists")
                if not ui.confirm("Continue anyway?"):
                    return
            
            ui.display_info(f"Would run: dotnet new {project_type} -n {project_name} -o {full_path}")
        
        # Install tools
        if ui.confirm("Install common .NET tools?"):
            tools = [
                "dotnet-ef", "dotnet-format", "dotnet-outdated",
                "dotnet-reportgenerator-globaltool", "dotnet-trace"
            ]
            
            selected_tools = ui.prompt_multichoice("Select tools to install:", tools)
            
            if selected_tools:
                for idx in selected_tools:
                    tool = tools[idx]
                    ui.display_info(f"Would run: dotnet tool install --global {tool}")
        
        ui.display_success(".NET environment configured successfully")