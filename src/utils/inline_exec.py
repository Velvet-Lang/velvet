import ast
import subprocess
import sys
from rich.console import Console
from rich.panel import Panel
from rich.theme import Theme
from typing import List, Tuple

cyber_theme = Theme({"info": "cyan blink", "error": "red bold", "success": "green"})
console = Console(theme=cyber_theme)

class InlineExecutor:
    def __init__(self):
        self.supported_langs = {"python", "shell", "rust", "js", "go", "cpp"}
        self.allow_langs = set()  # From flags

    def parse_flags(self):
        for arg in sys.argv[1:]:
            if arg.startswith('--allow-'):
                lang = arg.split('=')[1] if '=' in arg else arg.split('-')[-1]
                self.allow_langs.add(lang)

    def execute(self, blocks: List[Tuple[str, str]], file_path: str) -> bool:
        self.parse_flags()
        success = True
        for lang, code in blocks:
            if lang not in self.supported_langs:
                console.print(Panel(f"[{file_path}] Unsupported: {lang}", style="error"))
                success = False
                continue
            if lang not in self.allow_langs and lang != "python":  # Python always safe?
                console.print(Panel(f"[{file_path}] Blocked {lang} (use --allow-{lang})", style="warning"))
                continue

            console.print(Panel(f"[{file_path}] Exec {lang}...", style="info"))
            try:
                if lang == "python":
                    tree = ast.parse(code)
                    exec(compile(tree, f"<inline>", "exec"))
                elif lang == "shell":
                    result = subprocess.run(code, shell=True, capture_output=True, text=True)
                    if result.returncode != 0:
                        console.print(Panel(result.stderr, style="error"))
                        success = False
                    else:
                        console.print(Panel(result.stdout, style="success"))
                elif lang == "rust":
                    with open("tmp.rs", "w") as f: f.write(code)
                    subprocess.run(["rustc", "tmp.rs", "-o", "tmp"], check=True)
                    subprocess.run(["./tmp"], check=True)
                elif lang == "js":
                    subprocess.run(["node", "-e", code], check=True)
                elif lang == "go":
                    with open("tmp.go", "w") as f: f.write(f"package main\nimport \"fmt\"\nfunc main() {{\n{code}\n}}")
                    subprocess.run(["go", "run", "tmp.go"], check=True)
                elif lang == "cpp":
                    with open("tmp.cpp", "w") as f: f.write(f"#include <iostream>\nint main() {{\n{code}\nreturn 0;\n}}")
                    subprocess.run(["g++", "tmp.cpp", "-o", "tmp"], check=True)
                    subprocess.run(["./tmp"], check=True)
            except Exception as e:
                console.print(Panel(f"[{file_path}] {lang} error: {str(e)}", style="error"))
                success = False
        return success

if __name__ == "__main__":
    executor = InlineExecutor()
    # Stub blocks from parser
    sample_blocks = [("python", 'print("Hi")'), ("rust", 'println!("Rust!");')]
    executor.execute(sample_blocks, "test.vel")
