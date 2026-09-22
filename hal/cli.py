import typer
from pathlib import Path
import sys, subprocess
from rich import print

app = typer.Typer(help="HAL - Python dependency hell, finally fixed.")

def get_venv_python():
    win = Path(".hal/venv/Scripts/python.exe")
    unix = Path(".hal/venv/bin/python")
    if win.exists(): return str(win)
    if unix.exists(): return str(unix)
    return sys.executable

@app.command()
def init():
    print("[bold cyan]HAL initializing...[/bold cyan]")
    Path("pyproject.toml").write_text('[project]\nname="hal-project"\nversion="0.1.0"\ndependencies=[]\n', encoding="utf-8") if not Path("pyproject.toml").exists() else None
    venv_path = Path(".hal/venv")
    if not venv_path.exists():
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)

@app.command()
def add(packages: list[str] = typer.Argument(..., help="Packages to install")):
    from hal.resolver import SmartResolver
    resolver = SmartResolver(python_exe=get_venv_python())
    for pkg in packages:
        print(f"[cyan]Installing {pkg}...[/cyan]")
        resolver.install(pkg)

@app.command()
def doctor(fix: bool = typer.Option(False, "--fix")):
    from hal.resolver import SmartResolver
    r = SmartResolver(python_exe=get_venv_python())
    r.fix_all_from_check() if fix else r.diagnose()

@app.command()
def check():
    doctor(fix=False)

if __name__ == "__main__":
    app()
