import os
import importlib.util
import glob
from datetime import datetime
import time

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from yaspin import yaspin
import importlib.util
import sys

app = typer.Typer()
console = Console()

def load_script(script_path):
    spec = importlib.util.spec_from_file_location("module", script_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module.__name__] = module
    spec.loader.exec_module(module)
    return module

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    clear_screen()
    header = Panel(
        Text("Windows starterpack utilities", style="bold magenta"),
        subtitle=f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        expand=False
    )
    console.print(header)

def get_script_description(script_path):
    try:
        spec = importlib.util.spec_from_file_location("module", script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, "__doc__", "No description available.")
    except:
        return "Unable to load script description."

def display_menu(scripts):
    print_header()
    table = Table(title="Available Scripts", expand=True)
    table.add_column("Number", justify="right", style="cyan", no_wrap=True)
    table.add_column("Script Name", style="magenta")
    table.add_column("Description", style="green")

    for i, script in enumerate(scripts, 1):
        desc = get_script_description(script)
        script_name = os.path.basename(script).replace(".py", "").replace("_", " ").title()
        table.add_row(str(i), script_name, desc.strip() if desc else "No description available.")

    console.print(table)
    console.print("\n[bold cyan]0.[/bold cyan] Exit")
    console.print("[bold cyan]R.[/bold cyan] Refresh script list")
    console.print("[bold cyan]H.[/bold cyan] Help")

def run_script(script):
    print_header()
    script_name = os.path.basename(script).replace(".py", "").replace("_", " ",).title()
    console.print(f"\nRunning [bold magenta]{script_name}[/bold magenta]...")
    console.rule(style="yellow")
    
    with yaspin(text="Executing script    ", color="yellow") as spinner:
        try:
            module = load_script(script)
            if hasattr(module, 'main'):
                module.main()
            else:
                console.print("[bold yellow]Warning: No 'main' function found in the script.[/bold yellow]")
            spinner.ok("✅")
        except Exception as e:
            spinner.fail("❌")
            console.print(f"[bold red]An error occurred:[/bold red] {e}")
    
    console.rule(style="yellow")
    input("\nPress Enter to return to the main menu...")

def show_help():
    print_header()
    help_text = """
    [bold green]Help Information:[/bold green]
    1. Enter the number of the script you want to run.
    2. Enter '0' to exit the program.
    3. Enter 'R' to refresh the list of available scripts.
    4. Enter 'H' to display this help information.

    [italic]Note: Scripts should be placed in the same directory as this main script.[/italic]
    """
    console.print(Panel(help_text, expand=False))
    input("\nPress Enter to return to the main menu...")

@app.command()
def scaffold(script_name: str):
    """
    Create a new script with a basic structure.
    """
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{script_name}.py")
    
    if os.path.exists(script_path):
        console.print(f"[bold red]Error: Script '{script_name}.py' already exists.[/bold red]")
        raise typer.Exit(code=1)
    
    template = f'''"""
This is the {script_name} script.
Add your script description here.
"""

from rich.console import Console
from rich.prompt import Prompt

console = Console()

def main():
    console.print("[bold blue]Welcome to {script_name}![/bold blue]")
    # Add your code here

if __name__ == "__main__":
    main()
'''
    
    with open(script_path, 'w') as file:
        file.write(template)
    
    console.print(f"[bold green]Successfully created {script_name}.py[/bold green]")

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        scripts_dir = os.path.dirname(os.path.abspath(__file__))
        
        while True:
            scripts = glob.glob(os.path.join(scripts_dir, '*.py'))
            scripts = [script for script in scripts if os.path.basename(script) not in ['main.py', 'build_script.py', 'setup.py']]
            
            display_menu(scripts)
            choice = typer.prompt("\nEnter your choice").strip().lower()
            
            if choice == '0':
                console.print("[bold green]Windows starterpack CLI exiting...[/bold green]")
                raise typer.Exit()
            elif choice == 'r':
                with yaspin(text="Refreshing script list", color="blue") as spinner:
                    time.sleep(1)  # Simulating refresh process
                    spinner.ok("✅")
                continue
            elif choice == 'h':
                show_help()
            elif choice.isdigit() and 1 <= int(choice) <= len(scripts):
                run_script(scripts[int(choice) - 1])
            else:
                console.print("[bold red]Invalid choice. Please try again.[/bold red]")
                time.sleep(1)

if __name__ == "__main__":
    app()