import os
from dotenv import load_dotenv

load_dotenv()

API_HOST = os.getenv("ACCELER8_API_HOST")
if not API_HOST:
    raise RuntimeError("ACCELER8_API_HOST not set in .env")

AUTH_TOKEN = os.getenv("ACCELER8_TOKEN")
if not AUTH_TOKEN:
    raise RuntimeError("ACCELER8_TOKEN not set in .env")

HEADERS = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
}