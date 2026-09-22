"""
HAL Resolver - Python dependency conflicts ko AI se samjhta aur fix karta hai.
"""

import subprocess
import os
import re
import json
import sys
from pathlib import Path
from rich import print

class SmartResolver:
    def __init__(self, python_exe=None):
        self.api_key = os.environ.get("GROQ_API_KEY")
        # venv wala python use karo, warna system wala
        if python_exe:
            self.python_exe = str(python_exe)
        else:
            # auto-detect
            win = Path(".hal/venv/Scripts/python.exe")
            unix = Path(".hal/venv/bin/python")
            if win.exists():
                self.python_exe = str(win)
            elif unix.exists():
                self.python_exe = str(unix)
            else:
                self.python_exe = sys.executable

    def _run_pip(self, args, **kwargs):
        """Hamesha venv wale pip se chalao"""
        cmd = [self.python_exe, "-m", "pip"] + args
        return subprocess.run(cmd, capture_output=True, text=True, **kwargs)

    # ------------------------------------------------------------------
    # STEP 1: Seedha pip se install karne ki koshish
    # ------------------------------------------------------------------
    def install(self, package: str, _retry_count: int = 0, _max_retries: int = 2):
        print(f"[bold cyan]HAL is resolving: {package}...[/bold cyan]")

        try:
            result = self._run_pip(["install", package], timeout=300)
        except subprocess.TimeoutExpired:
            print(f"[bold red]HAL: {package} install mein 5 min se zyada lag raha hai.[/bold red]")
            return False
        except Exception as e:
            print(f"[bold red]HAL: Masla aaya: {e}[/bold red]")
            return False

        if result.returncode == 0:
            print(f"[bold green]SUCCESS: {package} installed! HAL wins where pip struggles.[/bold green]")
            return True

        print("[bold yellow]Conflict found. Trying to fix...[/bold yellow]")
        error_text = result.stderr[-2000:]

        if not self.api_key:
            print("[bold red]AI auto-fix band hai — GROQ_API_KEY set nahi hai.[/bold red]")
            print(result.stderr[-500:])
            return False

        suggestion = self._ask_ai_for_fix(package, error_text)
        if suggestion is None:
            print("[bold red]AI se fix nahi mila.[/bold red]")
            return False

        print(f"[bold green]HAL AI ka fix:[/bold green] {suggestion['explanation']}")

        if suggestion.get("fix_command") and _retry_count < _max_retries:
            print(f"[dim]Trying: pip install {suggestion['fix_command']}[/dim]")
            try:
                retry_result = self._run_pip(["install"] + suggestion["fix_command"].split(), timeout=300)
            except Exception as e:
                print(f"[bold red]Fix try mein masla: {e}[/bold red]")
                return False
            if retry_result.returncode == 0:
                print(f"[bold green]SUCCESS: HAL ne khud fix kar diya![/bold green]")
                return True
            else:
                print("[bold yellow]Ye fix kaam nahi aaya, dobara...[/bold yellow]")
                return self.install(package, _retry_count=_retry_count + 1, _max_retries=_max_retries)
        return False

    # ------------------------------------------------------------------
    # AI CALL
    # ------------------------------------------------------------------
    def _ask_ai_for_fix(self, package: str, error_text: str):
        try:
            import requests
        except ImportError:
            print("[bold red]'requests' missing — pip install requests karo.[/bold red]")
            return None

        prompt = (
            f"Tum Python dependency expert ho. '{package}' install pe ye error aaya:\n\n"
            f"{error_text}\n\n"
            "Sirf valid JSON return karo:\n"
            '{"explanation": "Roman Urdu mein 1-2 line", '
            '"fix_command": "package==version ya khaali"}\n'
        )

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": "openai/gpt-oss-120b",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 300,
                    "temperature": 0.2,
                },
                timeout=20,
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"].strip()
            content = re.sub(r"^```json\s*|\s*```$", "", content.strip())
            return json.loads(content)
        except Exception as e:
            print(f"[dim]AI call fail: {e}[/dim]")
            return None

    # ------------------------------------------------------------------