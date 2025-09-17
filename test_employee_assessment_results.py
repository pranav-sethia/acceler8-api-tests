# import requests
# import pytest
# import random
# import string
# import time
# from config import API_HOST, ORG_HEADERS as HEADERS

# ASSESS_URL = f"{API_HOST}/backend/v1/assessment"

# @pytest.fixture(scope="module")
# def employee_only_assessment_fixture():
#     rand_suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    
#     assess_body = {
#         "capabilities": ["TECHNICAL SKILLS 1"], 
#         "name": f"Employee-Only Test {rand_suffix}",
#         "show_onboarding": False, 
#         "assessment_type": "EMPLOYEE"
#     }
#     r_assess = requests.post(ASSESS_URL, json=assess_body, headers=HEADERS)
#     assert r_assess.status_code == 200, f"Failed to create assessment: {r_assess.text}"
#     assessment_id = r_assess.json()["data"]["id"]

#     onboarding_url = f"{ASSESS_URL}/{assessment_id}/onboarding/home"
#     onboarding_body = {
#         "program_name": "Employee-Only Program",
#         "service_personalization": [{"service": "LETTER_TO_YOURSELF", "position": 0}],
#         "number_of_days": 30
#     }
#     r_onboarding = requests.post(onboarding_url, json=onboarding_body, headers=HEADERS)
#     assert r_onboarding.status_code == 200, f"Failed to set up onboarding: {r_onboarding.text}"

#     q_url = f"{ASSESS_URL}/{assessment_id}/question"
#     q_body = {
#         "capabilities": "TECHNICAL SKILLS 1", "capabilities_label": "TECHNICAL SKILLS 1",
#         "sub_capability": "Calm and Composed", "visibility": ["EMPLOYEE"], "type": "OBJECTIVE_SINGLE",
#         "question": "How often do you remain calm?",
#         "options": [{"value": "Regularly", "input_required": False}], "ranking": [4], "sl_no": 1,
#         "capability_sl_no": 1, "sub_capability_sl_no": 1, "manager_question": None,
#         "manager_question_type": None, "manager_options": None, "manager_ranking": None
#     }
#     r_q = requests.post(q_url, json=q_body, headers=HEADERS)
#     assert r_q.status_code == 200, f"Failed to create question: {r_q.text}"
#     question_id = r_q.json()["id"]

#     emp_url = f"{ASSESS_URL}/{assessment_id}/employee"
#     emp_body = {
#         "email": f"emp_only_{rand_suffix}@example.com", "name": "Employee Only Submitter",
#         "manager": {"email": f"mgr_only_{rand_suffix}@example.com", "name": "Placeholder Manager"}
#     }
#     r_emp = requests.post(emp_url, json=emp_body, headers=HEADERS)
#     assert r_emp.status_code == 201, f"Failed to create employee: {r_emp.text}"
#     employee_id = r_emp.json()["data"]["id"]

#     submit_url = f"{API_HOST}/backend/v1/employee/{employee_id}/assessment/{assessment_id}/response"
#     submit_body = {
#         "responses": [{"question_id": question_id, "score": 0, "answer_text": None, "options": [{"option": "Regularly", "option_text": None}]}],
#         "status": "SUBMITTED", "assessment_type": "EMPLOYEE"
#     }
#     r_submit = requests.post(submit_url, json=submit_body, headers=HEADERS)
#     assert r_submit.status_code == 200, f"Failed to submit response: {r_submit.text}"
    
#     publish_url = f"{ASSESS_URL}/{assessment_id}/result/visibility"
#     publish_body = {"result_visibility": "MANAGER_AND_EMPLOYEE"}
#     r_publish = requests.put(publish_url, json=publish_body, headers=HEADERS)
#     assert r_publish.status_code == 200, f"Failed to publish result: {r_publish.text}"
    
#     time.sleep(2)

#     yield {"assessment_id": assessment_id, "employee_id": employee_id}

#     requests.delete(f"{ASSESS_URL}/{assessment_id}", headers=HEADERS)


# def test_employee_only_submission_is_captured(employee_only_assessment_fixture):
#     assessment_id = employee_only_assessment_fixture["assessment_id"]
#     employee_id = employee_only_assessment_fixture["employee_id"]
    
#     details_url = f"{API_HOST}/backend/v1/employee/{employee_id}/assessment/{assessment_id}?assessment_type=EMPLOYEE"
    
#     r_check = requests.get(details_url, headers=HEADERS)
#     assert r_check.status_code == 200, f"Failed to get details: {r_check.text}"
#     final_data = r_check.json()["data"]

#     assert final_data["sub_capabilities"][0]["response_captured"] is True


# def test_generate_ai_summary_for_employee(employee_only_assessment_fixture):
#     """
#     Tests the GET .../generate-ai endpoint for a single employee.
#     """
#     assessment_id = employee_only_assessment_fixture["assessment_id"]
#     employee_id = employee_only_assessment_fixture["employee_id"]

#     url = f"{API_HOST}/backend/v1/assessmentId/{assessment_id}/employee/{employee_id}/generate-ai"
    
#     params = {
#         "regenerate": True,
#         "model": "openai"
#     }

#     r = requests.get(url, params=params, headers=HEADERS)
#     assert r.status_code == 200, f"Failed to generate AI summary: {r.text}"

#     data = r.json()["data"]
#     assert "summary" in data
#     assert isinstance(data["summary"], str)
#     assert len(data["summary"]) > 0