import os
import certifi
from pathlib import Path
from dotenv import load_dotenv

# macOS SSL cert fix
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)

# Dual Model Architecture:
# Main Model: Qwen 2.5 Coder 14B (Coding & Complex tasks - 8.5GB VRAM)
# Aux Model: Gemma 2 2B (Ultra-fast simple chat & greetings - 1.5GB VRAM)
MLX_MAIN_MODEL = os.getenv("MLX_MAIN_MODEL", "mlx-community/Qwen2.5-Coder-14B-Instruct-4bit")
MLX_AUX_MODEL = os.getenv("MLX_AUX_MODEL", "mlx-community/gemma-2-2b-it-4bit")

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
