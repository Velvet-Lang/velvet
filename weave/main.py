import sys
from rich.console import Console
from rich.theme import Theme
from rich.panel import Panel
from rich.progress import Progress
import subprocess  # Call Rust/Zig

cyber_theme = Theme({
    "info": "cyan blink",
    "warning": "magenta",
    "danger": "red bold",
    "success": "green",
})

console = Console(theme=cyber_theme)

def build(project_name=None, flags=[]):
    with Progress() as progress:
        task = progress.add_task("[cyan]Weaving...", total=100)
        # Simulate steps
        progress.update(task, advance=20)
        console.print(Panel("Parsing .vel files...", style="info"))
        # Call velvet_parser.py
        subprocess.run(["python", "src/velvet_parser.py"])
        progress.update(task, advance=30)
        console.print(Panel("Checking errors...", style="warning"))
        # Call Rust for checks (like Cargo check)
        subprocess.run(["cargo", "run", "--bin", "weave_check"])
        progress.update(task, advance=20)
        if '--release' in flags:
            console.print(Panel("Optimizing for release...", style="success"))
        # Call Zig for codegen
        subprocess.run(["zig", "build-exe", "src/compiler.zig"])
        progress.update(task, advance=30)
        out_file = f"{project_name or 'app'}.weave" if not flags else f"{project_name or 'app'}.{flags[0].strip('--')}"
        console.print(Panel(f"Built: {out_file}", style="success"))

if __name__ == '__main__':
    args = sys.argv[1:]
    if args[0] == 'build':
        flags = [a for a in args[1:] if a.startswith('--')]
        project = args[1] if not flags else args[2] if len(args) > 2 else None
        build(project, flags)
    else:
        console.print("[danger]Invalid command. Use: weave build [project] [--flags][/danger]")
