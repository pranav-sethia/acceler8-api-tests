import requests
import json

API_HOST = "https://dev3.api.theacceler8.com"
AUTH_TOKEN = "eyJhbGciOiJIUzM4NCJ9.eyJzdWIiOiI0Y2I1ZGY2Zi1mNDJlLTRjODgtYWI1Ni1iMzcxNmMzMTgxYjAiLCJvcmdfaWQiOiJmNTc5MmQxYS1hMGQ5LTQ5ODctODQ0OS1kMzE5ZGU1MjlmNGUiLCJpYXQiOjE3NTIwMzc0MjUsImV4cCI6MTc1MjA0ODIyNX0.XnQfKNPY9LbVJ-ENh6JMxbr69VMBfDryt9oaa_A59Dv3vc862CcXjZxQfHIh_1yg"

def test_create_organization():
    url = f"{API_HOST}/backend/v1/organisation"

    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}"
    }

    body = {
        "internal_name": "Pranav3",
        "name": "Pranav4",
        "colour_theme": "DRIVEN_RED",
        "logo": "comet.jpg"
    }

    response = requests.post(url, json=body, headers=headers)
    data = response.json()

    assert response.status_code == 200, f"Request failed: {json.dumps(data, indent=2)}"

