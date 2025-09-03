import requests
import pytest
import json
import requests
import json
import pytest
import os

# Compulsory To Populate
API_HOST = "https://dev3.api.theacceler8.com"
AUTH_TOKEN = "eyJhbGciOiJIUzM4NCJ9.eyJzdWIiOiI0Y2I1ZGY2Zi1mNDJlLTRjODgtYWI1Ni1iMzcxNmMzMTgxYjAiLCJvcmdfaWQiOiJmNTc5MmQxYS1hMGQ5LTQ5ODctODQ0OS1kMzE5ZGU1MjlmNGUiLCJpYXQiOjE3NTMwOTY2ODUsImV4cCI6MTc1MzEwNzQ4NX0.p8sMyyh2uwWqmhYNW3vnY9XgY353PYrxxwlpwOspVL9JzXRu1-iJDTOLYvLKHAVk"
BASE_URL = f"{API_HOST}/backend/v1"
# ID of the Org to Switch to. Now all the Api calls will be made to this org
ORG_ID_TO_SWITCH = "fcedde1c-c1f0-4d4b-ad64-c0a8de4b8b1a"
SWITCH_BASE_URL = "https://dev3.api.theacceler8.com/backend/organisations"
TEST_FILE_PATH = "copy.xlsx"


ORG_AUTH_TOKEN = ""
# ID to be used for Employee Operations
EMPLOYEE_ID = ""
# Code to be used for Employee Operations
EMPLOYEE_CODE = ""
MANAGER_ID = ""
@pytest.fixture(scope="module")
def created_org():
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}"
    }
    body = {
        "internal_name": "TestEmployee",
        "name": "TestEmployee",
        "colour_theme": "DRIVEN_RED",
        "logo": "comet.jpg"
    }
    response = requests.post(BASE_URL+"/organisation", json=body, headers=headers)
    assert response.status_code == 200, f"Request failed: {json.dumps(response.json(), indent=2)}"
    org_id = response.json()["data"]["id"]
    yield org_id
    requests.delete(f"{BASE_URL}/organisation/{org_id}", headers=headers)


# Switch the Context to an Organisation
def test_switch_organisation():
    """
    Tests the PUT /organisations/switch endpoint to switch organizations.
    """
    global AUTH_TOKEN


    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Origin": "https://feature-novu.dxs9qirw787ss.amplifyapp.com",
        "DNT": "1",
        "Sec-GPC": "1",
        "Connection": "keep-alive",
        "Referer": "https://feature-novu.dxs9qirw787ss.amplifyapp.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "Priority": "u=0",
        "Content-Length": "0" # As per your curl request, there's no body
    }
   # https: // dev3.api.theacceler8.com / backend / organisations / switch?organisationId = fcedde1c - c1f0 - 4d4b - ad64 - c0a8de4b8b1a

    # Construct the URL with the query parameter
    url = f"{SWITCH_BASE_URL}/switch?organisationId={ORG_ID_TO_SWITCH}"

    response = requests.put(url, headers=headers)

    # Assert the status code is 200 for a successful switch
    assert response.status_code == 200, f"Organization switch failed: {json.dumps(response.json(), indent=2)}"

    response_data = response.json()
    # Switching the Context to Organisation

    AUTH_TOKEN = response_data["data"][0]["access_token"]

    # If the API returns a success message or specific data upon successful switch,
    # you can add further assertions here. For example:
    # assert response.json().get("message") == "Organisation switched successfully"
    print(f"Successfully switched to organization ID: {ORG_ID_TO_SWITCH}")


# TODO: ADD CREATE ASSESMENT APIS to the FLOW
ASSESSMENT_ID = "affb6ce2-5887-40b8-8363-3a8766a12bbd"

def test_upload_employee_assessment_file():
    """
    Tests the file upload endpoint for employee assessment.
    """

    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}"
        # For multipart/form-data, requests handles Content-Type automatically when using 'files'
    }

    # Ensure the file exists before attempting to open it
    if not os.path.exists(TEST_FILE_PATH):
        pytest.fail(f"Test file not found at: {TEST_FILE_PATH}")

    # Prepare the file for upload
    # 'file' is the name of the form field as specified in your curl command: --form 'file=@...'
    # files = {
    #     'file': , open(TEST_FILE_PATH, 'rb'))
    # }

    files = [
        ('file', (os.path.basename(TEST_FILE_PATH), open(TEST_FILE_PATH, 'rb'),
                  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))
    ]

    # Construct the URL
    url = f"{BASE_URL}/assessment/{ASSESSMENT_ID}/employee/upload"

    print(f"Attempting to upload file from: {TEST_FILE_PATH}")
    print(f"To URL: {url}")

    try:
        response = requests.post(url, headers=headers, files=files)

        # Assert the status code
        assert response.status_code == 200, \
            f"File upload failed with status code {response.status_code}: {json.dumps(response.json(), indent=2)}"

        # Optional: Assert on the response content if the API returns specific success data
        response_json = response.json()
        print(f"File upload successful. Response: {json.dumps(response_json, indent=2)}")
        assert response_json.get("status") == 200
        assert response_json.get("message") == "success"
        # Add more assertions based on the expected successful response structure

    except requests.exceptions.RequestException as e:
        pytest.fail(f"Request failed: {e}")
    finally:
        # Close the file object after the request is complete
        if 'file' in files and files['file'][1] and not files['file'][1].closed:
            files['file'][1].close()






def test_get_assessment_employees_pagination():
    """
    Tests fetching assessment employees with pagination, verifying status, structure, and data.
    """
    page_number = 1
    # ERROR: TODO: This seems like an error where the only value accepted by the platform is 10, and nothing else, can be verified by taking the test.
    # the Pagniation is working on the front-end. Need to check how that is working.
    page_size = 10

    url = f"{BASE_URL}/assessment/{ASSESSMENT_ID}/employees?page={page_number}&size={page_size}"

    headers = {
        'Authorization': f'Bearer {AUTH_TOKEN}'
    }

    print(f"\nMaking GET request to: {url}")
    response = requests.request("GET", url, headers=headers)

    # --- Pytest Assertions ---

    # 1. Assert HTTP Status Code
    # We expect a 200 OK status for a successful request.
    assert response.status_code == 200, \
        f"Expected status code 200, but got {response.status_code}. Response: {response.text}"

    # 2. Assert Response is Valid JSON
    try:
        response_json = response.json()
    except json.JSONDecodeError:
        pytest.fail(f"Response is not valid JSON. Response text: {response.text}")

    # 3. Assert Top-Level Structure
    # Check for expected keys at the root of the JSON response.
    expected_keys = ["status", "message", "data", "total_count", "total_pages", "current_page", "page_size"]
    for key in expected_keys:
        assert key in response_json, f"Missing expected key '{key}' in response."

    # 4. Assert Expected Values in Top-Level Structure
    assert response_json["status"] == 200, f"Expected 'status' to be 200, but got {response_json['status']}"
    assert response_json[
               "message"] == "success", f"Expected 'message' to be 'success', but got {response_json['message']}"
    assert response_json["current_page"] == page_number, \
        f"Expected 'current_page' to be {page_number}, but got {response_json['current_page']}"
    assert response_json["page_size"] == page_size, \
        f"Expected 'page_size' to be {page_size}, but got {response_json['page_size']}"

    # 5. Assert 'data' field is a list
    assert isinstance(response_json["data"],
                      list), f"Expected 'data' to be a list, but got {type(response_json['data'])}"

    # 6. Assert 'data' list contains expected number of items (based on page_size)
    # This assertion only makes sense if total_count is >= page_size
    if response_json["total_count"] > 0:
        assert len(response_json["data"]) == page_size, \
            f"Expected 'data' list to contain {page_size} item(s), but got {len(response_json['data'])}"
    else:
        assert len(response_json["data"]) == 0, "Expected 'data' list to be empty when total_count is 0."
    # 7. Assert Structure of each item in 'data' (if data is not empty)
    if response_json["data"]:
        first_employee = response_json["data"][0]
        # Assuming an employee object has at least an 'id', 'name', 'email' etc.
        # Adjust these keys based on your actual employee object structure.
        expected_employee_keys = ["id", "name", "email"]  # Add more as per your API response for an employee
        for key in expected_employee_keys:
            assert key in first_employee, f"Missing expected key '{key}' in first employee data item."

        # Example: Check if ID is a valid UUID format (optional, requires regex or specific library)
        # assert isinstance(first_employee["id"], str) and len(first_employee["id"]) == 36

    global MANAGER_ID
    MANAGER_ID = response_json["data"][0]["manager"]["id"]
    print("API Response Assertions Passed!")
    # print(json.dumps(response_json, indent=2)) # Uncomment to print the formatted response if needed




def test_create_employee_for_assessment():
    """
    Tests the POST /assessment/{ASSESSMENT_ID}/employee endpoint to create a new employee.
    """
    url = f"{BASE_URL}/assessment/{ASSESSMENT_ID}/employee"

    # Define the payload as a Python dictionary
    payload_data = {
        "email": "kaustubhparmar99+3AT6@gmail.com",  # Consider making this unique for each test run if needed
        "name": "E1",
        "position": "A",
        "title": "A",
        "number_of_direct_reports": "1",
        "number_of_indirect_reports": "1",
        "join_date": "2025-06-01",
        "tenure": 1,
        "years_to_retirement": 1,
        "manager": {
            "email": "kaustubh+manager306@tccapita.com",
            "name": "A",
            "position": "A",
            "title": "A",
            "number_of_direct_reports": None,
            "number_of_indirect_reports": None,
            "join_date": None,
            "tenure": None,
            "years_to_retirement": None,
            "performance_rating": None,
            "voice_of_customer_results": None,
            "team_attrition_rate_current_year": None,
            "team_attrition_rate_previous_year": None,
            "voice_of_employee_results": None
        },
        "performance_rating": "1",
        "voice_of_customer_results": "1",
        "team_attrition_rate_current_year": "1",
        "team_attrition_rate_previous_year": "1",
        "voice_of_employee_results": "1"
    }

    headers = {
        'Authorization': f'Bearer {AUTH_TOKEN}',
        'Content-Type': 'application/json'
    }

    print(f"\nMaking POST request to: {url}")
    # requests.post is more idiomatic for POST requests
    # json=payload_data automatically sets Content-Type to application/json
    response = requests.post(url, headers=headers, json=payload_data)

    # --- Pytest Assertions ---

    # 1. Assert HTTP Status Code
    # For a successful creation, usually 200 OK or 201 Created is expected.
    # Check your API documentation for the exact expected success code.
    assert response.status_code == 201, \
        f"Expected status code 201, but got {response.status_code}. Response: {response.text}"

    # 2. Assert Response is Valid JSON
    try:
        response_json = response.json()
    except json.JSONDecodeError:
        pytest.fail(f"Response is not valid JSON. Response text: {response.text}")

    # 3. Assert Top-Level Structure
    # Check for expected keys at the root of the JSON response.
    # A typical successful creation might return the created object.
    # Adjust these keys based on your actual API response for a successful employee creation.
    expected_keys = ["status", "message", "data"]
    for key in expected_keys:
        assert key in response_json, f"Missing expected key '{key}' in response."

    # 4. Assert Expected Values in Top-Level Structure
    assert response_json["status"] == 200, f"Expected 'status' to be 200, but got {response_json['status']}"
    assert response_json[
               "message"] == "success", f"Expected 'message' to be 'success', but got {response_json['message']}"

    # 5. Assert 'data' field structure and content (assuming 'data' contains the created employee)
    assert isinstance(response_json["data"],
                      dict), f"Expected 'data' to be a dictionary, but got {type(response_json['data'])}"

    created_employee = response_json["data"]

    # Assert that the created employee has an 'id' (UUID)
    assert "id" in created_employee, "Missing 'id' in created employee data."
    assert isinstance(created_employee["id"], str), "Employee 'id' is not a string."
    # Basic UUID format check (length and segments)
    assert len(created_employee["id"]) == 36 and '-' in created_employee["id"], \
        f"Employee 'id' {created_employee['id']} does not appear to be a valid UUID."

    # Assert that key fields from the payload are reflected in the response
    assert created_employee.get("email").lower() == payload_data["email"].lower(), "Created employee email mismatch."
    assert created_employee.get("name") == payload_data["name"], "Created employee name mismatch."
    # Add more assertions for other important fields you sent in the payload
    # For example:
    # assert created_employee.get("position") == payload_data["position"]

    print("Employee Creation API Assertions Passed!")
    # print(json.dumps(response_json, indent=2)) # Uncomment to print the formatted response if needed

    global EMPLOYEE_ID
    EMPLOYEE_ID = created_employee['id']

    # Optional: If you need to clean up the created employee after the test,
    # you can return the employee_id and use it in a fixture with teardown logic.
    # For simplicity, this example just performs the creation and asserts.





def test_update_assessment_employee():
    """
    Tests the PUT /assessment/{ASSESSMENT_ID}/employee/{EMPLOYEE_ID} endpoint to update an employee.
    """
    url = f"{BASE_URL}/assessment/{ASSESSMENT_ID}/employee/{EMPLOYEE_ID}"

    # Define the payload as a Python dictionary
    payload_data = {
        "name": "updated e1", # Updated name
        "position": "B",
        "title": "A",
        "number_of_direct_reports": 1,
        "number_of_indirect_reports": 1,
        "join_date": "2025-06-16",
        "tenure": 1,
        "years_to_retirement": 1,
        "manager_email": "kaustubh+3ta1@tccapita.com",
        "performance_rating": "1",
        "voice_of_customer_results": "1",
        "team_attrition_rate_current_year": "1",
        "team_attrition_rate_previous_year": "1",
        "voice_of_employee_results": "1"
    }

    headers = {
        'Authorization': f'Bearer {AUTH_TOKEN}',
        'Content-Type': 'application/json'
    }

    print(f"\nMaking PUT request to: {url}")
    # requests.put is more idiomatic for PUT requests
    # json=payload_data automatically sets Content-Type to application/json
    response = requests.put(url, headers=headers, json=payload_data)

    # --- Pytest Assertions ---

    # 1. Assert HTTP Status Code
    # For a successful update, usually 200 OK or 204 No Content is expected.
    # If the API returns the updated resource, 200 OK is common.
    # If it just confirms success without a body, 204 No Content.
    assert response.status_code == 200, \
        f"Expected status code 200, but got {response.status_code}. Response: {response.text}"

    # 2. Assert Response is Valid JSON (if status code is 200 and response body is expected)
    # If the API returns 204 No Content, there will be no response.json()
    if response.status_code == 200:
        try:
            response_json = response.json()
        except json.JSONDecodeError:
            pytest.fail(f"Response is not valid JSON. Response text: {response.text}")

        # 3. Assert Top-Level Structure
        # Check for expected keys at the root of the JSON response.
        # A typical successful update might return the updated object or a success message.
        expected_keys = ["status", "message", "data"] # Adjust based on your API's actual success response
        for key in expected_keys:
            assert key in response_json, f"Missing expected key '{key}' in response."

        # 4. Assert Expected Values in Top-Level Structure
        assert response_json["status"] == 200, f"Expected 'status' to be 200, but got {response_json['status']}"
        assert response_json["message"] == "success", f"Expected 'message' to be 'success', but got {response_json['message']}"

        # 5. Assert 'data' field structure and content (assuming 'data' contains the updated employee)
        assert isinstance(response_json["data"], dict), f"Expected 'data' to be a dictionary, but got {type(response_json['data'])}"

        updated_employee = response_json["data"]

        # Assert that the updated employee's ID matches the one in the URL
        assert updated_employee.get("id") == EMPLOYEE_ID, "Updated employee ID mismatch."

        # Assert that key fields from the payload are reflected in the response
        assert updated_employee.get("name") == payload_data["name"], "Updated employee name mismatch."
        assert updated_employee.get("position") == payload_data["position"], "Updated employee position mismatch."
        assert updated_employee.get("join_date") == payload_data["join_date"], "Updated employee join_date mismatch."
        global EMPLOYEE_CODE
        EMPLOYEE_CODE = updated_employee.get("employee_code")
        # Add more assertions for other important fields you sent in the payload
        # For example, for manager_email, note that your API might transform it to a nested 'manager' object.
        # You'd need to inspect the actual response to assert its structure.
        # Example if manager_email becomes manager.email in response:
        # assert updated_employee.get("manager", {}).get("email") == payload_data["manager_email"]


    print("Employee Update API Assertions Passed!")
    # print(json.dumps(response_json, indent=2)) # Uncomment to print the formatted response if needed


#
# # Define a path to save the exported file for verification
# DOWNLOAD_DIR = "downloaded_exports"
# # Create the directory if it doesn't exist
# if not os.path.exists(DOWNLOAD_DIR):
#     os.makedirs(DOWNLOAD_DIR)
# '''
# def test_export_assessment_employees_all():
#     """
#     Tests the POST /assessment/{ASSESSMENT_ID}/employee/export endpoint
#     to export all employees, verifying status, content type, and file download.
#     """
#     url = f"{BASE_URL}/assessment/{ASSESSMENT_ID}/employee/export"
#
#     payload_data = {
#         "select_all": True
#     }
#     headers = {
#         'Authorization': f'Bearer {AUTH_TOKEN}',
#         'Content-Type': 'application/json'
#     }
#
#     print(f"\nMaking POST request to: {url} for export...")
#     response = requests.post(url, headers=headers, json=payload_data)
#
#     # --- Pytest Assertions ---
#
#     # 1. Assert HTTP Status Code
#     # A successful file export usually returns 200 OK.
#     assert response.status_code == 200, \
#         f"Expected status code 200 for export, but got {response.status_code}. Response: {response.text}"
#
#     # 2. Assert Content-Type Header for file download
#     # Expecting an Excel (xlsx) or CSV content type.
#     # Common Excel MIME types: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#     # Common CSV MIME types: 'text/csv'
#     content_type = response.headers.get('Content-Type', '')
#     print(f"Received Content-Type: {content_type}")
#     assert 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' in content_type or \
#            'text/csv' in content_type, \
#            f"Expected Content-Type for Excel/CSV, but got: {content_type}"
#
#     # 3. Assert Content-Disposition Header for filename (optional but good practice)
#     # This header typically suggests the filename for download.
#     content_disposition = response.headers.get('Content-Disposition', '')
#     print(f"Received Content-Disposition: {content_disposition}")
#     assert 'attachment' in content_disposition, "Content-Disposition header does not indicate attachment."
#     assert 'filename=' in content_disposition, "Content-Disposition header does not contain a filename."
#
#     # Optional: Extract filename from Content-Disposition and verify extension
#     if 'filename=' in content_disposition:
#         filename_start_index = content_disposition.find('filename=') + len('filename=')
#         # Remove quotes if present
#         filename = content_disposition[filename_start_index:].strip('"')
#         print(f"Suggested filename: {filename}")
#         assert filename.endswith(('.xlsx', '.csv')), \
#             f"Expected filename to end with .xlsx or .csv, but got: {filename}"
#
#         # 4. Save the file and verify its existence (important for export tests)
#         file_path = os.path.join(DOWNLOAD_DIR, filename)
#         with open(file_path, 'wb') as f:
#             f.write(response.content)
#
#         assert os.path.exists(file_path), f"Exported file was not saved at: {file_path}"
#         assert os.path.getsize(file_path) > 0, f"Exported file is empty: {file_path}"
#         print(f"Exported file successfully saved to: {file_path}")
#
#         # Optional: Basic check of file content (e.g., if it's an Excel/CSV,
#         # you might try to open it with pandas for more detailed assertions)
#         # For this example, we just check size > 0.
#     else:
#         pytest.fail("Could not extract filename from Content-Disposition header.")
#
#     print("Employee Export API Assertions Passed!")
#
#     # Teardown: Clean up the downloaded file after the test
#     # This can also be done via a Pytest fixture for more robust cleanup.
#     # try:
#     #     if os.path.exists(file_path):
#     #         os.remove(file_path)
#     #         print(f"Cleaned up downloaded file: {file_path}")
#     # except Exception as e:
#     #     print(f"Error during cleanup of {file_path}: {e}")
# '''
#
# # TODO: Above verify the content type header and resolve issue using wrong header.
# # TODO: and add email result link endpoint to test, Notify employee endpoint to test
# # and Employee and manager result link endpoint
#
#
# # Note: Your curl request did not include an Authorization header,
# # but it's common for APIs to require it. If you encounter 401/403 errors,
# # you'll need to add an AUTH_TOKEN here.
# # AUTH_TOKEN = "your_auth_token_here"

def test_get_employee_by_code():
    """
    Tests the GET /assessment/{ASSESSMENT_ID}/employee/by_code endpoint
    to retrieve an employee by their unique code.
    """
    url = f"{BASE_URL}/assessment/{ASSESSMENT_ID}/employee/by_code?code={EMPLOYEE_CODE}"


    headers = {
        'Authorization': f'Bearer {AUTH_TOKEN}'
    }

    print(f"\nMaking GET request to: {url} to retrieve employee by code...")
    response = requests.request("GET", url, headers=headers)

    # --- Pytest Assertions ---

    # 1. Assert HTTP Status Code
    # Expect a 200 OK status for a successful retrieval.
    assert response.status_code == 200, \
        f"Expected status code 200, but got {response.status_code}. Response: {response.text}"

    # 2. Assert Response is Valid JSON
    try:
        response_json = response.json()
    except json.JSONDecodeError:
        pytest.fail(f"Response is not valid JSON. Response text: {response.text}")

    # 3. Assert Top-Level Structure
    # Check for expected keys at the root of the JSON response.
    # Assuming a structure like: {"status": 200, "message": "success", "data": {...}}
    expected_top_level_keys = ["status", "message", "data"]
    for key in expected_top_level_keys:
        assert key in response_json, f"Missing expected top-level key '{key}' in response."

    # 4. Assert Expected Values in Top-Level Structure
    assert response_json["status"] == 200, f"Expected 'status' to be 200, but got {response_json['status']}"
    assert response_json["message"] == "success", f"Expected 'message' to be 'success', but got {response_json['message']}"

    # 5. Assert 'data' field structure and content
    # The 'data' field should contain the employee object.
    assert isinstance(response_json["data"], dict), f"Expected 'data' to be a dictionary (employee object), but got {type(response_json['data'])}"

    employee_data = response_json["data"]

    # Assert that the retrieved employee has expected keys (e.g., id, name, email)
    # Adjust these keys based on the actual structure of an employee object returned by your API.
    expected_employee_keys = ["id", "name", "email", "position"]
    for key in expected_employee_keys:
        assert key in employee_data, f"Missing expected key '{key}' in employee data: {json.dumps(employee_data, indent=2)}"

    # Assert that the code in the response matches the requested code
    # This assumes the API returns the employee code within the employee_data.
    # If the 'code' is not directly in the returned employee object, you might skip this or
    # look for it in a different part of the response or related object.
    # For example, if it's nested under a field like 'assessment_details' or similar.
    # Assuming for now it might be directly in the employee_data, or you need to
    # confirm how the API relates the 'code' to the returned employee.
    # If 'code' is returned as a field in the employee object:
    assert employee_data.get("employee_code") == EMPLOYEE_CODE, "Retrieved employee code mismatch."

    print("Employee Retrieval by Code API Assertions Passed!")
    # print(json.dumps(response_json, indent=2)) # Uncomment to print the formatted response if needed







def test_get_employee_by_id():
    """
    Tests the GET /employee/employee/{employeeId} endpoint to retrieve a single employee by ID.
    """
    url = f"{BASE_URL}/employee/{EMPLOYEE_ID}"


    headers = {
        'Authorization': f'Bearer {AUTH_TOKEN}'
    }

    print(f"\nMaking GET request to: {url} to retrieve employee by ID...")
    response = requests.request("GET", url, headers=headers)

    # --- Pytest Assertions ---

    # 1. Assert HTTP Status Code
    # Expect a 200 OK status for a successful retrieval.
    assert response.status_code == 200, \
        f"Expected status code 200, but got {response.status_code}. Response: {response.text}"

    # 2. Assert Response is Valid JSON
    try:
        response_json = response.json()
    except json.JSONDecodeError:
        pytest.fail(f"Response is not valid JSON. Response text: {response.text}")

    # 3. Assert Top-Level Structure
    # Assuming a structure like: {"status": 200, "message": "success", "data": {...}}
    expected_top_level_keys = ["status", "message", "data"]
    for key in expected_top_level_keys:
        assert key in response_json, f"Missing expected top-level key '{key}' in response."

    # 4. Assert Expected Values in Top-Level Structure
    assert response_json["status"] == 200, f"Expected 'status' to be 200, but got {response_json['status']}"
    assert response_json["message"] == "success", f"Expected 'message' to be 'success', but got {response_json['message']}"

    # 5. Assert 'data' field structure and content
    # The 'data' field should contain the employee object.
    assert isinstance(response_json["data"], dict), \
        f"Expected 'data' to be a dictionary (employee object), but got {type(response_json['data'])}"

    employee_data = response_json["data"]

    # Assert that the retrieved employee's ID matches the one requested
    assert employee_data.get("id") == EMPLOYEE_ID, \
        f"Retrieved employee ID '{employee_data.get('id')}' does not match requested ID '{EMPLOYEE_ID}'."

    # Assert that the retrieved employee has expected keys (e.g., name, email, position)
    # Adjust these keys based on the actual structure of an employee object returned by your API.
    expected_employee_keys = ["name", "email", "position"] # Add more as relevant
    for key in expected_employee_keys:
        assert key in employee_data, f"Missing expected key '{key}' in employee data: {json.dumps(employee_data, indent=2)}"

    # Example: Assert on a specific value, e.g., that the name is not empty
    assert employee_data.get("name") is not None and employee_data.get("name") != "", \
        "Employee name should not be empty."

    print("Employee Retrieval by ID API Assertions Passed! 🎉")
    # print(json.dumps(response_json, indent=2)) # Uncomment to print the formatted response if needed




#

def test_verify_employee_assessment():
    """
    Tests the POST /assessment/{ASSESSMENT_ID}/employee/{EMPLOYEE_ID}/verify endpoint.
    This endpoint likely triggers a verification process or marks an employee as verified.
    """
    url = f"{BASE_URL}/assessment/{ASSESSMENT_ID}/employee/{EMPLOYEE_ID}/verify"

    headers = {}
    # If an Authorization header is required, uncomment and add it:
    # headers = {
    #     'Authorization': f'Bearer {AUTH_TOKEN}'
    # }

    # For a POST request with an empty payload, data=payload or json={} can be used.
    # json={} is often clearer if no body content is truly intended.
    payload_data = {} # Represents an empty JSON body

    print(f"\nMaking POST request to: {url} to verify employee...")
    response = requests.post(url, headers=headers, json=payload_data)

    # --- Pytest Assertions ---

    # 1. Assert HTTP Status Code
    # For a successful verification, usually 200 OK is expected.
    # Check your API documentation for the exact expected success code.
    assert response.status_code == 200, \
        f"Expected status code 200 for verification, but got {response.status_code}. Response: {response.text}"

    # 2. Assert Response is Valid JSON (if status code is 200 and response body is expected)
    if response.status_code == 200:
        try:
            response_json = response.json()
        except json.JSONDecodeError:
            pytest.fail(f"Response is not valid JSON. Response text: {response.text}")

        # 3. Assert Top-Level Structure
        # Assuming a structure like: {"status": 200, "message": "success", "data": {...}}
        expected_top_level_keys = ["status", "message"] # Adjust based on your API's actual success response
        # The 'data' field might be present, or not, for a 'verify' operation.
        # If 'data' is expected and contains the updated employee status, add it to expected_top_level_keys
        # and add assertions for its content.
        if "data" in response_json:
            expected_top_level_keys.append("data")

        for key in expected_top_level_keys:
            assert key in response_json, f"Missing expected top-level key '{key}' in response."

        # 4. Assert Expected Values in Top-Level Structure
        assert response_json["status"] == 200, f"Expected 'status' to be 200, but got {response_json['status']}"
        assert response_json["message"] == "success", f"Expected 'message' to be 'success', but got {response_json['message']}"

        # 5. Assert 'data' field content (if present and relevant for verification)
        # If the API returns the updated employee object or verification status in 'data':
        if "data" in response_json and isinstance(response_json["data"], dict):
            verified_data = response_json["data"]
            # Example: If the response includes the employee ID or a 'verified' status
            # assert verified_data.get("employee_id") == EMPLOYEE_ID
            # assert verified_data.get("is_verified") == True # Assuming a boolean field

            # You'll need to inspect your API's actual successful response body
            # for this endpoint to write specific assertions here.
            print(f"Data in response: {json.dumps(verified_data, indent=2)}")

    print("Employee Verification API Assertions Passed! ✅")
    # print(response.text) # Uncomment to print the raw response if needed



def test_get_employee_assessments():
    """
    Tests the GET /employee/{EMPLOYEE_ID}/assessments endpoint to retrieve
    a list of assessments associated with a specific employee.
    """
    url = f"{BASE_URL}/employee/{EMPLOYEE_ID}/assessments"

    headers = {}
    # If an Authorization header is required, uncomment and add it:
    # headers = {
    #     'Authorization': f'Bearer {AUTH_TOKEN}'
    # }

    print(f"\nMaking GET request to: {url} to retrieve employee assessments...")
    response = requests.request("GET", url, headers=headers)

    # --- Pytest Assertions ---

    # 1. Assert HTTP Status Code
    # Expect a 200 OK status for a successful retrieval.
    assert response.status_code == 200, \
        f"Expected status code 200, but got {response.status_code}. Response: {response.text}"

    # 2. Assert Response is Valid JSON
    try:
        response_json = response.json()
    except json.JSONDecodeError:
        pytest.fail(f"Response is not valid JSON. Response text: {response.text}")

    # 3. Assert Top-Level Structure
    # Assuming a common structure like: {"status": 200, "message": "success", "data": [...]}
    expected_top_level_keys = ["status", "message", "data", "total_count", "total_pages", "current_page",
                               "page_size"]
    for key in expected_top_level_keys:
        assert key in response_json, f"Missing expected top-level key '{key}' in response."

    # 4. Assert Expected Values in Top-Level Structure
    assert response_json["status"] == 200, f"Expected 'status' to be 200, but got {response_json['status']}"
    assert response_json[
               "message"] == "success", f"Expected 'message' to be 'success', but got {response_json['message']}"

    # Assert pagination details
    assert isinstance(response_json["total_count"], int), "Expected 'total_count' to be an integer."
    assert isinstance(response_json["total_pages"], int), "Expected 'total_pages' to be an integer."
    assert isinstance(response_json["current_page"], int), "Expected 'current_page' to be an integer."
    assert isinstance(response_json["page_size"], int), "Expected 'page_size' to be an integer."

    # You might want to assert specific page/size if passed as query params, e.g.:
    # assert response_json["current_page"] == 0 # Or whatever your default is

    # 5. Assert 'data' field is a list
    assert isinstance(response_json["data"], list), \
        f"Expected 'data' to be a list of assessments, but got {type(response_json['data'])}"

    # 6. Assert content of the 'data' list (if not empty)
    if response_json["data"]:
        # Iterate through each assessment in the list and assert its structure
        for i, assessment in enumerate(response_json["data"]):
            assert isinstance(assessment, dict), f"Assessment item at index {i} is not a dictionary."

            # Assert key fields for each assessment object
            expected_assessment_keys = [
                "id", "name",
                "status",  "created_at", "updated_at",
            ]
            for key in expected_assessment_keys:
                assert key in assessment, f"Assessment item at index {i} missing expected key '{key}'."

            # Example: Assert on the type of ID and status field for each assessment
            assert isinstance(assessment["id"], str), f"Assessment ID at index {i} is not a string."
            assert isinstance(assessment["status"], str), f"Assessment status at index {i} is not a string."
            # Add more specific value assertions if relevant, e.g., if a certain assessment should always be active
            # assert assessment["is_active"] == True # If expected

    else:
        print("No assessments found for this employee. Skipping data content assertions.")
        # If no assessments are expected, you might specifically assert total_count == 0

    print("Employee Assessments API Assertions Passed! ✅")
    # print(json.dumps(response_json, indent=2)) # Uncomment to print the formatted response if needed



def test_get_manager_subordinates():
    """
    Tests the GET /assessment/{ASSESSMENT_ID}/manager/{MANAGER_ID}/subordinates endpoint.
    Verifies the list of subordinates returned for a given manager.
    """
    url = f"{BASE_URL}/assessment/{ASSESSMENT_ID}/manager/{MANAGER_ID}/subordinates"

    headers = {}
    # If an Authorization header is required, uncomment and add it:
    # headers = {
    #     'Authorization': f'Bearer {AUTH_TOKEN}'
    # }

    print(f"\nMaking GET request to: {url} to retrieve manager's subordinates...")
    response = requests.request("GET", url, headers=headers)

    # --- Pytest Assertions ---

    # 1. Assert HTTP Status Code
    assert response.status_code == 200, \
        f"Expected status code 200, but got {response.status_code}. Response: {response.text}"

    # 2. Assert Response is Valid JSON
    try:
        response_json = response.json()
    except json.JSONDecodeError:
        pytest.fail(f"Response is not valid JSON. Response text: {response.text}")

    # 3. Assert Top-Level Structure
    expected_top_level_keys = ["status", "message", "data", "total_count", "total_pages", "current_page", "page_size"]
    for key in expected_top_level_keys:
        assert key in response_json, f"Missing expected top-level key '{key}' in response."

    # 4. Assert Expected Values in Top-Level Structure
    assert response_json["status"] == 200, f"Expected 'status' to be 200, but got {response_json['status']}"
    assert response_json[
               "message"] == "success", f"Expected 'message' to be 'success', but got {response_json['message']}"

    # Note: total_count, total_pages, etc., are 0 in your sample response for this endpoint's top-level.
    # The actual count of subordinates is nested. Assert these as per your sample.
    assert response_json["total_count"] == 0, f"Expected 'total_count' to be 0, but got {response_json['total_count']}"
    assert response_json["total_pages"] == 0, f"Expected 'total_pages' to be 0, but got {response_json['total_pages']}"
    assert response_json[
               "current_page"] == 0, f"Expected 'current_page' to be 0, but got {response_json['current_page']}"
    assert response_json["page_size"] == 0, f"Expected 'page_size' to be 0, but got {response_json['page_size']}"

    # 5. Assert 'data' field structure and content (manager and their subordinates)
    assert isinstance(response_json["data"], dict), \
        f"Expected 'data' to be a dictionary, but got {type(response_json['data'])}"

    manager_and_subordinates_data = response_json["data"]

    # Assert the manager's own data within the 'data' object
    assert manager_and_subordinates_data.get("id") == MANAGER_ID, \
        f"Manager ID in response '{manager_and_subordinates_data.get('id')}' does not match requested ID '{MANAGER_ID}'."
    # assert manager_and_subordinates_data.get("email") == "kaustubh+3ta1@tccapita.com", "Manager email mismatch."
    # assert manager_and_subordinates_data.get("name") == "Kaustubh Manager 1", "Manager name mismatch."
    # assert manager_and_subordinates_data.get("role") == "MANAGER_ONLY", "Manager role mismatch."
    assert manager_and_subordinates_data.get("assessment_id") == ASSESSMENT_ID, "Manager assessment_id mismatch."

    # Assert 'subordinates' key is present and is a list
    assert "subordinates" in manager_and_subordinates_data, "Missing 'subordinates' key in manager data."
    assert isinstance(manager_and_subordinates_data["subordinates"], list), \
        f"Expected 'subordinates' to be a list, but got {type(manager_and_subordinates_data['subordinates'])}"

    subordinates_list = manager_and_subordinates_data["subordinates"]

    # Assert a minimum number of subordinates if you expect some always
    assert len(subordinates_list) > 0, "Expected to find some subordinates, but the list is empty."

    # Assert the count of subordinates as per the sample response (12 subordinates in your sample)
    assert len(subordinates_list) == 12, f"Expected 12 subordinates, but found {len(subordinates_list)}."

    # Assert structure and content of the first subordinate (and optionally others)
    if subordinates_list:
        first_subordinate = subordinates_list[0]
        assert isinstance(first_subordinate, dict), "First subordinate item is not a dictionary."

        expected_subordinate_keys = [
            "subordinates", "id", "email", "name", "position", "status",
            "role", "assessment_id", "manager_assessed"
        ]
        for key in expected_subordinate_keys:
            assert key in first_subordinate, f"Missing expected key '{key}' in first subordinate data."

        # # Assert specific values of the first subordinate from your sample
        # assert first_subordinate.get("id") == "832cd294-6772-4ad7-ac62-7d08c34b4c3a", "First subordinate ID mismatch."
        # assert first_subordinate.get("email") == "kaustubhparmar99+3ta2@gmail.com", "First subordinate email mismatch."
        # assert first_subordinate.get("name") == "Kaustubh 2", "First subordinate name mismatch."
        # assert first_subordinate.get("status") == "CREATED", "First subordinate status mismatch."
        # assert first_subordinate.get("role") == "EMPLOYEE", "First subordinate role mismatch."
        # assert first_subordinate.get("manager_assessed") is False, "First subordinate manager_assessed mismatch."

        # Example of iterating and checking properties for all subordinates (more robust)
        for sub in subordinates_list:
            assert "id" in sub
            assert "email" in sub
            assert isinstance(sub.get("email"), str)
            assert sub.get("email") is not None and "@" in sub.get("email")  # Basic email format check
            # assert sub.get("role") == "EMPLOYEE"  # All are expected to be employees

    print("Manager Subordinates API Assertions Passed! ✅")
    # print(json.dumps(response_json, indent=2)) # Uncomment to print the formatted response if needed
