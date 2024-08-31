"""
Activates Windows 10 Pro
"""

import os
from time import sleep

from rich.console import Console
from rich.prompt import Prompt

console = Console()

def main():
    console.print("[bold blue]Activating Windows and restarting the system[/bold blue]")
    console.print("[bold red]Please wait...[/bold red]")

    # Available keys: https://passper.imyfone.com/windows-10/windows-10-product-key-free/
    os.system("slmgr /ipk W269N-WFGWX-YVC9B-4J6C9-T83GX")
    os.system("slmgr /skms kms8.msguides.com")
    os.system("slmgr /ato")

    console.print("[bold green]Windows has been activated successfully![/bold green]")
    console.print("[bold red]Restarting the system...[/bold red]")
    sleep(3)

    os.system("shutdown /r /t 0")

if __name__ == "__main__":
    main()

