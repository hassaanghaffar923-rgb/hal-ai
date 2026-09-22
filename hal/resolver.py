"""
HAL Resolver - Python dependency conflicts ko AI se samjhta aur fix karta hai.
"""
import subprocess, os, re, json, sys
from pathlib import Path
from rich import print

class SmartResolver:
    def __init__(self, python_exe=None):
        self.api_key = os.environ.get("GROQ_API_KEY")
        if python_exe:
            self.python_exe = str(python_exe)
        else:
            win = Path(".hal/venv/Scripts/python.exe")
            unix = Path(".hal/venv/bin/python")
            if win.exists():
                self.python_exe = str(win)
            elif unix.exists():
                self.python_exe = str(unix)
            else:
                self.python_exe = sys.executable

    def _run_pip(self, args, **kwargs):
        cmd = [self.python_exe, "-m", "pip"] + args
        return subprocess.run(cmd, capture_output=True, text=True, **kwargs)

    def install(self, package: str, _retry_count: int = 0, _max_retries: int = 2):
        print(f"[bold cyan]HAL is resolving: {package}...[/bold cyan]")
        try:
            result = self._run_pip(["install", package], timeout=300)
        except Exception as e:
            print(f"[bold red]Masla: {e}[/bold red]")
            return False
        if result.returncode == 0:
            print(f"[bold green]SUCCESS: {package} installed![/bold green]")
            return True
        print("[yellow]Conflict, AI se fix try...[/yellow]")
        error_text = result.stderr[-2000:]
        if not self.api_key:
            print(result.stderr[-500:])
            return False
        suggestion = self._ask_ai_for_fix(package, error_text)
        if suggestion and suggestion.get("fix_command"):
            print(f"[green]AI Fix: {suggestion['fix_command']}[/green]")
            retry = self._run_pip(["install"] + suggestion["fix_command"].split(), timeout=300)
            if retry.returncode == 0:
                print("[bold green]SUCCESS: AI ne fix kar diya![/bold green]")
                return True
        return False

    def _ask_ai_for_fix(self, package: str, error_text: str):
        try:
            import requests
        except:
            return None
        prompt = f"Python error for '{package}':\n{error_text}\nReturn JSON: {{\"explanation\":\"Roman Urdu\",\"fix_command\":\"pkg==ver\"}}"
        try:
            import re, json
            r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization": f"Bearer {self.api_key}"}, json={"model": "openai/gpt-oss-120b", "messages": [{"role": "user", "content": prompt}], "max_tokens": 300}, timeout=20)
            c = r.json()["choices"][0]["message"]["content"].strip()
            c = re.sub(r"^`json\s*|\s*`$", "", c)
            return json.loads(c)
        except Exception as e:
            print(f"[dim]AI fail: {e}[/dim]")
            return None

    def fix_all_from_check(self):
        print("[bold cyan]HAL Doctor --fix mode (SMART)[/bold cyan]")
        result = self._run_pip(["check"])
        output = result.stdout.strip()
        if not output or "No broken" in output:
            print("[bold green]All good! No broken requirements.[/bold green]")
            return
        print(f"[yellow]{output}[/yellow]\n")
        # SMART FIX: googletrans purana hai to usko upgrade karo, httpx ko downgrade mat karo
        if "googletrans" in output and "httpx" in output:
            print("[cyan]HAL SMART FIX: googletrans purana hai, isko naya kar raha hu...[/cyan]")
            self.install("googletrans==4.0.0rc1")
            return

        for line in output.splitlines():
            m = re.search(r"has requirement\s+([^,]+)", line)
            if not m:
                m = re.search(r"requires\s+(.+)", line)
            if m:
                req = m.group(1).strip().split(",")[0].strip()
                print(f"[cyan]Fixing {req}...[/cyan]")
                self.install(req)

    def diagnose(self):
        result = self._run_pip(["check"])
        output = result.stdout.strip()
        if not output or "No broken" in output:
            print("[bold green]All good! No conflicts found.[/bold green]")
            return
        print(f"[bold yellow]{output}[/bold yellow]")
        print("[dim]Run: hal doctor --fix for auto-fix[/dim]")

