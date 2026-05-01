import os
from dotenv import load_dotenv

load_dotenv()

# ===== APIS =====
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
FREEPIK_API_KEY = os.getenv("FREEPIK_API_KEY")
REPLICATE_API_KEY = os.getenv("REPLICATE_API_KEY", "")

# ===== FREEPIK =====
FREEPIK_BASE_URL = "https://api.freepik.com/v1"
FREEPIK_IMAGE_GEN = f"{FREEPIK_BASE_URL}/images/generate"
FREEPIK_VIDEO_GEN = f"{FREEPIK_BASE_URL}/videos/generate"

# ===== VIDEO SPECS =====
VIDEO_WIDTH = 720
VIDEO_HEIGHT = 1280
VIDEO_FPS = 24
VIDEO_DURATION_MIN = 6
VIDEO_DURATION_MAX = 15

# ===== COLOR GRADING =====
COLOR_GRADING = {
    "contraste": 1.15,
    "saturacao": 1.1,
    "brilho": 1.0
}

print("✓ Config loaded!")
