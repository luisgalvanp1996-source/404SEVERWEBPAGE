import requests
from bot.config import FLASK_API_BASE

def post(endpoint, data):
    r = requests.post(f"{FLASK_API_BASE}{endpoint}", json=data, timeout=5)
    r.raise_for_status()
    return r.json()

def get(endpoint):
    r = requests.get(f"{FLASK_API_BASE}{endpoint}", timeout=5)
    r.raise_for_status()
    return r.json()
