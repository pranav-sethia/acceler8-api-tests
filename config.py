"""
Configuration file for Acceler8 API tests
Handles authentication and organization switching
"""
import os
from dotenv import load_dotenv
import requests

load_dotenv()

# API configuration from environment variables
API_HOST = os.getenv("ACCELER8_API_HOST")
if not API_HOST:
    raise RuntimeError("ACCELER8_API_HOST not set in .env")

AUTH_TOKEN = os.getenv("ACCELER8_TOKEN")
if not AUTH_TOKEN:
    raise RuntimeError("ACCELER8_TOKEN not set in .env")

# Default headers for API requests
HEADERS = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
}

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
if not AUTH_TOKEN:
    raise RuntimeError("ACCELER8_TOKEN not set in .env")

ORG_ID = os.getenv("ORG_ID")

# Cache for organization-specific headers
_ORG_HEADERS_CACHE = {}

def org_headers(org_id: str | None = None, *, force_refresh: bool = False) -> dict:
    """
    Get headers for a specific organization
    Switches to the organization and returns auth headers
    """
    target = org_id or ORG_ID
    if not target:
        raise RuntimeError("No org_id provided and ORG_ID not set in .env")

    # Return cached headers if available
    if not force_refresh and target in _ORG_HEADERS_CACHE:
        return _ORG_HEADERS_CACHE[target]

    # Switch to organization and get new token
    url = f"{API_HOST}/backend/organisations/switch"
    r = requests.put(url, params={"organisationId": target}, headers=HEADERS, timeout=30)
    r.raise_for_status()

    token = r.json()["data"][0]["access_token"]
    print(token)  # Debug: print token for verification
    hdrs = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    _ORG_HEADERS_CACHE[target] = hdrs
    return hdrs

# Default organization headers for tests
ORG_HEADERS = org_headers()
    