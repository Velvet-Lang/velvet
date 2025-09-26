import ast
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.theme import Theme
from typing import List, Tuple

cyber_theme = Theme({
    "info": "cyan blink",
    "error": "red bold",
    "success": "green",
})

console = Console(theme=cyber_theme)

class InlineExecutor:
    def __init__(self):
        self.supported_langs = {"python", "shell"}  # Extend as needed

    def execute(self, blocks: List[Tuple[str, str]], file_path: str) -> bool:
        success = True
        for lang, code in blocks:
            if lang not in self.supported_langs:
                console.print(
                    Panel(
                        f"[{file_path}] Unsupported inline language: {lang}",
                        style="error",
                    )
                )
                success = False
                continue

            console.print(
                Panel(f"[{file_path}] Executing inline {lang} block...", style="info")
            )

            try:
                if lang == "python":
                    # Safe eval for demo (use ast.literal_eval for production)
                    tree = ast.parse(code)
                    exec(compile(tree, f"<inline_{lang}>", "exec"))
                elif lang == "shell":
                    result = subprocess.run(
                        code, shell=True, capture_output=True, text=True
                    )
                    if result.returncode != 0:
                        console.print(
                            Panel(
                                f"[{file_path}] Shell error: {result.stderr}",
                                style="error",
                            )
                        )
                        success = False
                    else:
                        console.print(
                            Panel(result.stdout, style="success")
                        )
            except Exception as e:
                console.print(
                    Panel(f"[{file_path}] {lang} error: {str(e)}", style="error")
                )
                success = False

        return success

if __name__ == "__main__":
    executor = InlineExecutor()
    sample_blocks = [
        ("python", 'print("Hello from inline Python!")'),
        ("shell", 'echo "Hello from inline Shell!"'),
        ("unknown", "invalid code"),
    ]
    executor.execute(sample_blocks, "test.vel")
