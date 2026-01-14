import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")

# IDs de admin (separados por coma en .env)
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x]

FLASK_API_BASE = os.getenv("FLASK_API_BASE", "http://127.0.0.1:5001/api")

EMOJI_CART = "🛒"
EMOJI_OK = "✅"
EMOJI_ERR = "❌"
