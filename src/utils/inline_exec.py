import ast
import subprocess
import sys
import os
import uuid
import shutil
from rich.console import Console
from rich.panel import Panel
from rich.theme import Theme
from typing import List, Tuple, Dict

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

    def execute(self, blocks: List[Tuple[str, str]], file_path: str) -> Dict[int, Dict[str, Any]]:
        self.parse_flags()
        results = {}
        tmp_dir = f"tmp_inline_{uuid.uuid4()}"
        os.makedirs(tmp_dir, exist_ok=True)
        try:
            for i, (lang, code) in enumerate(blocks):
                if lang not in self.supported_langs:
                    console.print(Panel(f"[{file_path}] Unsupported: {lang}", style="error"))
                    continue
                if lang not in self.allow_langs:
                    console.print(Panel(f"[{file_path}] Blocked {lang} (use --allow-{lang})", style="warning"))
                    continue

                console.print(Panel(f"[{file_path}] Exec {lang}...", style="info"))
                tmp_file = os.path.join(tmp_dir, f"inline_{i}.{self.get_ext(lang)}")
                with open(tmp_file, "w") as f:
                    f.write(self.wrap_code(lang, code))
                cmd = self.get_cmd(lang, tmp_file)
                env = os.environ.copy()
                env['PATH'] = '/usr/bin:/bin'  # Limited for security
                env['NO_NETWORK'] = '1'  # Stub sandbox
                proc_result = subprocess.run(cmd, capture_output=True, text=True, env=env, shell=False if lang not in {'shell', 'powershell'} else True)
                if os.path.exists("tmp"):
                    os.remove("tmp")
                results[i] = {'stdout': proc_result.stdout.strip(), 'stderr': proc_result.stderr.strip(), 'code': proc_result.returncode}
                if proc_result.returncode != 0:
                    console.print(Panel(f"[{file_path}] {lang} error: {proc_result.stderr}", style="error"))
                else:
                    console.print(Panel(proc_result.stdout, style="success"))
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)
        return results

    def get_ext(self, lang):
        return {
            "python": "py", "shell": "sh", "rust": "rs", "powershell": "ps1",
            "go": "go", "crystal": "cr", "ruby": "rb", "c": "c", "cpp": "cpp",
            "csharp": "cs", "julia": "jl", "zig": "zig", "lua": "lua",
            "java": "java", "javascript": "js"
        }.get(lang, "txt")

    def wrap_code(self, lang, code):
        if lang == "python":
            return code
        if lang == "c":
            return f"#include <stdio.h>\nint main() {{ {code} return 0; }}"
        if lang == "cpp":
            return f"#include <iostream>\nint main() {{ {code} return 0; }}"
        if lang == "java":
            return f"public class Tmp {{ public static void main(String[] args) {{ {code} }} }}"
        if lang == "csharp":
            return f"using System; class Tmp {{ static void Main() {{ {code} }} }}"
        if lang == "rust":
            return f"fn main() {{ {code} }}"
        if lang == "go":
            return f"package main\nimport \"fmt\"\nfunc main() {{ {code} }}"
        if lang == "zig":
            return f"pub fn main() !void {{ {code} }}"
        # Others no wrap needed
        return code

    def get_cmd(self, lang, file):
        if lang == "python": return ["python", file]
        if lang == "shell": return ["bash", file]
        if lang == "powershell": return ["powershell", "-File", file]
        if lang == "rust": return ["rustc", file, "-o", "tmp"]
        if lang == "go": return ["go", "run", file]
        if lang == "crystal": return ["crystal", "run", file]
        if lang == "ruby": return ["ruby", file]
        if lang == "c": return ["gcc", file, "-o", "tmp"]
        if lang == "cpp": return ["g++", file, "-o", "tmp"]
        if lang == "csharp": return ["csc", file, "&&", "mono", "tmp.exe"]
        if lang == "julia": return ["julia", file]
        if lang == "zig": return ["zig", "run", file]
        if lang == "lua": return ["lua", file]
        if lang == "java": return ["javac", file, "&&", "java", "Tmp"]
        if lang == "javascript": return ["node", file]
        return []

if __name__ == "__main__":
    executor = InlineExecutor()
    sample_blocks = [("python", 'print("Hello from inline Python!")')]
    executor.execute(sample_blocks, "test.vel")
