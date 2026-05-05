import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ===== APIS =====
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
FREEPIK_API_KEY = os.getenv("FREEPIK_API_KEY")
REPLICATE_API_KEY = os.getenv("REPLICATE_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")

# ===== FREEPIK =====
FREEPIK_BASE_URL = "https://api.freepik.com/v1"
FREEPIK_IMAGE_GEN = f"{FREEPIK_BASE_URL}/images/generate"
FREEPIK_VIDEO_GEN = f"{FREEPIK_BASE_URL}/videos/generate"

# ===== EXTERNAL REPOSITORIES =====
BASE_DIR = Path(__file__).parent
EXTERNAL_DIR = BASE_DIR / "external"
VIDEO_USE_PATH = EXTERNAL_DIR / "video-use"
HYPERFRAMES_PATH = EXTERNAL_DIR / "hyperframes"

# ===== WORKSPACE =====
WORKSPACE_DIR = BASE_DIR / "workspace"
WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)

# ===== VIDEO SPECS =====
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
VIDEO_FPS = 24
VIDEO_DURATION_MIN = 6
VIDEO_DURATION_MAX = 120

# ===== COLOR GRADING =====
COLOR_GRADING = {
    "contraste": 1.15,
    "saturacao": 1.1,
    "brilho": 1.0
}

print("✓ Config loaded!")
