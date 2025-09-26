import click
from rich.console import Console
from rich.panel import Panel
from rich.theme import Theme
import subprocess
import sys

cyber_theme = Theme({"run": "blue bold underline", "debug": "magenta blink"})
console = Console(theme=cyber_theme)

@click.group()
def cli():
    pass

@cli.command()
@click.argument('project')
def run(project):
    console.print(Panel(f"Running {project} in cyber mode...", style="run"))
    # Interpret .weave or .vel
    subprocess.run([sys.executable, "src/velvet_parser.py", project, "--exec"])
    console.print(Panel("Execution complete.", style="success"))

@cli.command()
@click.argument('project')
def debug(project):
    console.print(Panel(f"Debug {project}: Neon traces...", style="debug"))
    # Enhanced: Step-through, vars dump
    subprocess.run([sys.executable, "src/utils/inline_exec.py", "--allow-all", project])
    # Add Rich live display

if __name__ == '__main__':
    cli()
