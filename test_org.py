import requests
import pytest
import json

from config import API_HOST, HEADERS

BASE_URL = f"{API_HOST}/backend/v1/organisation"

@pytest.fixture(scope="module")
def created_org():
    body = {
        "internal_name": "TestInternal",
        "name": "TestOrg",
        "colour_theme": "DRIVEN_RED",
        "logo": "comet.jpg"
    }
    response = requests.post(BASE_URL, json=body, headers=HEADERS)
    assert response.status_code == 200, f"Request failed: {json.dumps(response.json(), indent=2)}"
    org_id = response.json()["data"]["id"]

    yield org_id
    requests.delete(f"{BASE_URL}/{org_id}", headers=HEADERS)

def test_get_org_details(created_org):
    response = requests.get(f"{BASE_URL}/{created_org}", headers=HEADERS)
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "TestOrg"

def test_update_org(created_org):
    updated_body = {
        "internal_name": "UpdatedInternal",
        "name": "UpdatedOrg",
        "colour_theme": "DRIVEN_RED",
        "logo": "comet.jpg"
    }
    response = requests.put(f"{BASE_URL}/{created_org}", json=updated_body, headers=HEADERS)
    assert response.status_code == 200

    confirm = requests.get(f"{BASE_URL}/{created_org}", headers=HEADERS)
    assert confirm.json()["data"]["name"] == "UpdatedOrg"

def test_delete_org():
    body = {
        "internal_name": "TempDelete",
        "name": "ToBeDeleted",
        "colour_theme": "DRIVEN_RED",
        "logo": "comet.jpg"
    }
    res = requests.post(BASE_URL, json=body, headers=HEADERS)
    assert res.status_code == 200
    org_id = res.json()["data"]["id"]

    del_res = requests.delete(f"{BASE_URL}/{org_id}", headers=HEADERS)
    assert del_res.status_code == 204

    get_res = requests.get(f"{BASE_URL}/{org_id}", headers=HEADERS)
    assert get_res.status_code == 404