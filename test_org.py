API_HOST = "https://dev3.api.theacceler8.com"
AUTH_TOKEN = "eyJhbGciOiJIUzM4NCJ9.eyJzdWIiOiI0Y2I1ZGY2Zi1mNDJlLTRjODgtYWI1Ni1iMzcxNmMzMTgxYjAiLCJvcmdfaWQiOiJmNTc5MmQxYS1hMGQ5LTQ5ODctODQ0OS1kMzE5ZGU1MjlmNGUiLCJpYXQiOjE3NTIwNTI3ODQsImV4cCI6MTc1MjA2MzU4NH0.XZprKjqM9wRVKBtpmpKZxYgxTzQ5r9hcDi8NzXhijple5IWZPPFEgplX9e9eaRKq"

BASE_URL = f"{API_HOST}/backend/v1/organisation"

@pytest.fixture(scope="module")
def created_org():
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}"
    }
    body = {
        "internal_name": "TestInternal",
        "name": "TestOrg",
        "colour_theme": "DRIVEN_RED",
        "logo": "comet.jpg"
    }
    response = requests.post(BASE_URL, json=body, headers=headers)
    assert response.status_code == 200
    org_id = response.json().get("id")
    yield org_id
    requests.delete(f"{BASE_URL}/{org_id}", headers=headers)

def test_get_org_details(created_org):
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}"
    }
    response = requests.get(f"{BASE_URL}/{created_org}", headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "TestOrg"

def test_update_org(created_org):
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}"
    }
    updated_body = {
        "internal_name": "UpdatedInternal",
        "name": "UpdatedOrg",
        "colour_theme": "GROWTH_GREEN",
        "logo": "rocket.jpg"
    }
    response = requests.put(f"{BASE_URL}/{created_org}", json=updated_body, headers=headers)
    assert response.status_code == 200

    confirm = requests.get(f"{BASE_URL}/{created_org}", headers=headers)
    assert confirm.json()["name"] == "UpdatedOrg"

def test_delete_org():
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}"
    }
    body = {
        "internal_name": "TempDelete",
        "name": "ToBeDeleted",
        "colour_theme": "COOL_BLUE",
        "logo": "temp.jpg"
    }
    res = requests.post(BASE_URL, json=body, headers=headers)
    assert res.status_code == 200
    org_id = res.json().get("id")

    del_res = requests.delete(f"{BASE_URL}/{org_id}", headers=headers)
    assert del_res.status_code == 200

    get_res = requests.get(f"{BASE_URL}/{org_id}", headers=headers)
    assert get_res.status_code == 404
