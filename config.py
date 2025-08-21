import os
from dotenv import load_dotenv
import requests

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

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
if not AUTH_TOKEN:
    raise RuntimeError("ACCELER8_TOKEN not set in .env")

ORG_ID = os.getenv("ORG_ID")

_ORG_HEADERS_CACHE = {}

def org_headers(org_id: str | None = None, *, force_refresh: bool = False) -> dict:
    target = org_id or ORG_ID
    if not target:
        raise RuntimeError("No org_id provided and ORG_ID not set in .env")

    if not force_refresh and target in _ORG_HEADERS_CACHE:
        return _ORG_HEADERS_CACHE[target]

    url = f"{API_HOST}/backend/organisations/switch"
    r = requests.put(url, params={"organisationId": target}, headers=HEADERS, timeout=30)
    r.raise_for_status()

    token = r.json()["data"][0]["access_token"]
    print(token)
    hdrs = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    _ORG_HEADERS_CACHE[target] = hdrs
    return hdrs

ORG_HEADERS = org_headers()
    