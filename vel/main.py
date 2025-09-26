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
    # Existing...

@cli.command()
@click.argument('project')
def debug(project):
    # Existing...

@cli.command()
def update():
    console.print(Panel("Updating libs via weave...", style="info"))
    subprocess.run(["cargo", "run", "--", "update"])

@cli.command()
def repl():
    console.print(Panel("Velvet REPL (cyberpunk mode)...", style="run"))
    while True:
        code = input(">> ")
        if code == "exit": break
        # Parse + exec inline/stub
        parser = VelvetParser()
        ast = parser.parse(code)
        # Exec...

if __name__ == '__main__':
    cli()
