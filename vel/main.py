import click
from rich.console import Console
from rich.panel import Panel
from rich.theme import Theme
import subprocess
import sys
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from velvet_parser import VelvetParser
from velvet_ir_gen import VelvetIRGen
from utils.inline_exec import InlineExecutor
import threading
import watchfiles
import os

cyber_theme = Theme({"run": "blue bold underline", "debug": "magenta blink", "info": "cyan", "success": "green", "error": "red"})
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

@cli.command()
def update():
    console.print(Panel("Updating libs via weave...", style="info"))
    subprocess.run(["cargo", "run", "--", "update"])

@cli.command()
def repl():
    console.print(Panel("Velvet REPL (cyberpunk mode)...", style="run"))
    session = PromptSession(history=FileHistory('.velvet_history'))
    executor = InlineExecutor()
    parser = VelvetParser()
    ir_gen = VelvetIRGen  # Class reference
    modules = {}  # path: ast

    def interpret(ast):
        ir = ir_gen(ast).generate()
        inline_results = executor.execute([(i['lang'], i['code']) for i in ir['inline']], "repl.vel")
        env = {}  # Stub env for vars/funcs
        for node in ir['nodes']:
            if node['type'] == 'var':
                env[node['name']] = node['expr']  # Eval stub
            elif node['type'] == 'func':
                # Call stub
                pass
            elif node['type'] == 'match':
                # Eval match
                pass
            elif node['type'] == 'if':
                # Eval cond
                pass
            elif node['type'] == 'loop':
                # Loop exec
                pass
            elif node['type'] == 'pattern':
                # Destruct
                pass
            # Async: Thread stub
            if 'async' in node and node['async']:
                # Threading.thread
                pass
        return f"Executed with inline results: {inline_results}"

    def load_module(path):
        if not os.path.exists(path):
            console.print(Panel(f"Module {path} not found", style="error"))
            return None
        with open(path, 'r') as f:
            code = f.read()
        ast = parser.parse(code)
        modules[path] = ast
        console.print(Panel(f"Loaded module {path}", style="success"))
        return ast

    def watch_modules():
        for changes in watchfiles.watch(*modules.keys()):
            for change_type, changed_path in changes:
                if change_type == watchfiles.Change.modified:
                    load_module(changed_path)
                    console.print(Panel(f"Reloaded {changed_path}", style="info"))

    threading.Thread(target=watch_modules, daemon=True).start()

    while True:
        try:
            code = session.prompt(">> ", auto_suggest=AutoSuggestFromHistory())
            if code.strip() == "exit": break
            if code.startswith("import "):
                path = code.split(maxsplit=1)[1].strip('"')
                load_module(path)
                continue
            ast = parser.parse(code)
            result = interpret(ast)
            console.print(Panel(result, style="success"))
        except Exception as e:
            console.print(Panel(str(e), style="error"))

if __name__ == '__main__':
    cli()
