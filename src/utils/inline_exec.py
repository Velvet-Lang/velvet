import ast
import subprocess
import sys
import os
from rich.console import Console
from rich.panel import Panel
from rich.theme import Theme
from typing import List, Tuple

cyber_theme = Theme({"info": "cyan blink", "error": "red bold", "success": "green"})
console = Console(theme=cyber_theme)

class InlineExecutor:
    def __init__(self):
        self.supported_langs = {
            "python", "shell", "rust", "powershell", "go", "crystal", "ruby",
            "c", "cpp", "csharp", "julia", "zig", "lua", "java", "javascript"
        }
        self.allow_langs = set()

    def parse_flags(self):
        for arg in sys.argv[1:]:
            if arg.startswith('--allow-'):
                lang = arg.split('-')[-1]
                self.allow_langs.add(lang)

    def execute(self, blocks: List[Tuple[str, str]], file_path: str) -> bool:
        self.parse_flags()
        success = True
        for lang, code in blocks:
            if lang not in self.supported_langs:
                console.print(Panel(f"Unsupported: {lang}", style="error"))
                success = False
                continue
            if lang not in self.allow_langs:
                console.print(Panel(f"Blocked {lang} (use --allow-{lang})", style="warning"))
                continue

            console.print(Panel(f"Exec {lang}...", style="info"))
            try:
                tmp_file = f"tmp.{self.get_ext(lang)}"
                with open(tmp_file, "w") as f:
                    f.write(self.wrap_code(lang, code))
                cmd = self.get_cmd(lang, tmp_file)
                result = subprocess.run(cmd, capture_output=True, text=True)
                os.remove(tmp_file)
                if lang in {"c", "cpp", "rust", "go", "zig", "java", "csharp"}:
                    os.remove("tmp")  # Exec binary
                if result.returncode != 0:
                    console.print(Panel(result.stderr, style="error"))
                    success = False
                else:
                    console.print(Panel(result.stdout, style="success"))
            except Exception as e:
                console.print(Panel(f"{lang} error: {str(e)}", style="error"))
                success = False
        return success

    def get_ext(self, lang):
        return {
            "python": "py", "shell": "sh", "rust": "rs", "powershell": "ps1",
            "go": "go", "crystal": "cr", "ruby": "rb", "c": "c", "cpp": "cpp",
            "csharp": "cs", "julia": "jl", "zig": "zig", "lua": "lua",
            "java": "java", "javascript": "js"
        }.get(lang, "txt")

    def wrap_code(self, lang, code):
        if lang == "c":
            return f"#include <stdio.h>\nint main() {{ {code} return 0; }}"
        elif lang == "cpp":
            return f"#include <iostream>\nint main() {{ {code} return 0; }}"
        elif lang == "java":
            return f"public class Tmp {{ public static void main(String[] args) {{ {code} }} }}"
        elif lang == "csharp":
            return f"using System; class Tmp {{ static void Main() {{ {code} }} }}"
        # Add wrappers for others if needed
        return code

    def get_cmd(self, lang, file):
        if lang == "python": return ["python", file]
        elif lang == "shell": return ["bash", file]
        elif lang == "powershell": return ["powershell", "-File", file]
        elif lang == "rust": return ["rustc", file, "-o", "tmp"]
        elif lang == "go": return ["go", "run", file]
        elif lang == "crystal": return ["crystal", "run", file]
        elif lang == "ruby": return ["ruby", file]
        elif lang == "c": return ["gcc", file, "-o", "tmp"]
        elif lang == "cpp": return ["g++", file, "-o", "tmp"]
        elif lang == "csharp": return ["csc", file]  # Assume mono/csc
        elif lang == "julia": return ["julia", file]
        elif lang == "zig": return ["zig", "run", file]
        elif lang == "lua": return ["lua", file]
        elif lang == "java": return ["javac", file, "&&", "java", "Tmp"]
        elif lang == "javascript": return ["node", file]
        return []

# Usage...
