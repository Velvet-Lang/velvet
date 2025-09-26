import sys
from rich.console import Console
from rich.theme import Theme
from rich.panel import Panel
import subprocess  # Simulate run

cyber_theme = Theme({"run": "blue bold underline"})

console = Console(theme=cyber_theme)

def run(project):
    console.print(Panel(f"Velvet Runner: Executing {project} in cyber mode...", style="run"))
    # Placeholder: Interpret .weave (slower)
    subprocess.run(["python", "-m", "interpreter", project])  # Hypothetical

if __name__ == '__main__':
    if len(sys.argv) > 1:
        run(sys.argv[1])
    else:
        console.print("[red]Usage: vel <project>[/red]")
