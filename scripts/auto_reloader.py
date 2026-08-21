import sys
import time
import subprocess
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
MAIN_SCRIPT = PROJECT_DIR / "main.py"
VENV_PYTHON = PROJECT_DIR / "venv" / "bin" / "python"

def get_latest_mtime() -> float:
    """Finds the latest modification time among all .py files in the project."""
    max_mtime = 0.0
    for path in PROJECT_DIR.rglob("*.py"):
        if "venv" in str(path):
            continue
        try:
            mtime = path.stat().st_mtime
            if mtime > max_mtime:
                max_mtime = mtime
        except Exception:
            pass
    return max_mtime

def run_auto_reloader():
    print("🔄 [AE Auto-Reloader] Initializing Hot-Reloading File Watcher...")
    print(f"📁 Watching directory: {PROJECT_DIR}")
    
    last_mtime = get_latest_mtime()
    process = subprocess.Popen([str(VENV_PYTHON), str(MAIN_SCRIPT), "--discord"], cwd=str(PROJECT_DIR))
    print("🚀 [AE Auto-Reloader] Discord Bot launched!")

    try:
        while True:
            time.sleep(1.0)
            current_mtime = get_latest_mtime()
            if current_mtime > last_mtime:
                print("\n⚡ [AE Auto-Reloader] Code modification detected! Reloading Discord Bot autonomously...")
                last_mtime = current_mtime
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                
                time.sleep(0.5)
                process = subprocess.Popen([str(VENV_PYTHON), str(MAIN_SCRIPT), "--discord"], cwd=str(PROJECT_DIR))
                print("✅ [AE Auto-Reloader] Discord Bot successfully restarted with updated code!\n")
    except KeyboardInterrupt:
        print("\nStopping Auto-Reloader...")
        process.terminate()

if __name__ == "__main__":
    run_auto_reloader()
