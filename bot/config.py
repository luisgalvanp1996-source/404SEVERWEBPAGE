#config.py

import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Emojis reutilizables
EMOJI_CART = "🛒"
EMOJI_ADD = "➕"
EMOJI_TRASH = "🗑️"
EMOJI_MONEY = "💰"
