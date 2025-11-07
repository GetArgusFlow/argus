# tests/test_parser.py

import pytest
import httpx
import json
from pathlib import Path

# Configuration for the test
SERVICE_URL = "http://localhost:8002/api/v1/parse"
TEST_CASES_DIR = Path(__file__).parent / "test_cases"

# This uses the default key from config.yml
DEV_API_KEY = "default_dev_key"
HEADERS = {"x-api-key": DEV_API_KEY}


def find_test_cases():
    """Finds all subdirectories in the test_cases directory."""
    if not TEST_CASES_DIR.is_dir():
        return []
    return [d for d in TEST_CASES_DIR.iterdir() if d.is_dir()]

@pytest.mark.parametrize("test_case_dir", find_test_cases())
def test_parser_with_case(test_case_dir: Path):
    """
    A data-driven test that runs for each test case directory.
    Pytest will call this function once for every folder found.
    """
    input_html_path = test_case_dir / "input.html"
    expected_json_path = test_case_dir / "expected_output.json"

    # 1. Check if the required files for the test case exist
    assert input_html_path.exists(), f"Missing input.html in {test_case_dir.name}"
    assert expected_json_path.exists(), f"Missing expected_output.json in {test_case_dir.name}"

    # 2. Read the test case data
    html_content = input_html_path.read_text(encoding='utf-8')
    with open(expected_json_path, 'r', encoding='utf-8') as f:
        expected_output = json.load(f)

    # 3. Prepare and send the request to the service
    payload = {"html_snippet": html_content}

    try:
        response = httpx.post(SERVICE_URL, json=payload, timeout=60.0, headers=HEADERS)
        response.raise_for_status()
    except httpx.RequestError as e:
        pytest.fail(f"Request failed for test case '{test_case_dir.name}': {e}")

    # 4. Get the actual result and compare it to the "golden" expected result
    actual_output = response.json()

    # Pytest will show a detailed "diff" if the dictionaries do not match
    assert actual_output == expected_output, f"Output for '{test_case_dir.name}' did not match expected_output.json"
    
    print(f"\n Test Passed: {test_case_dir.name}")

@pytest.mark.parametrize("headers", [
    pytest.param({}, id="no_key_provided"),
    pytest.param({"x-api-key": "this-is-the-wrong-key"}, id="wrong_key_provided")
])
def test_parse_fails_with_bad_auth(headers):
    """
    Tests that the /parse endpoint fails with 401 if auth is missing or wrong.
    """
    payload = {"html_snippet": "<div></div>"}
    
    response = httpx.post(SERVICE_URL, json=payload, headers=headers)
    
    # We MUST get a 401 Unauthorized error
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    # Check that the error message is correct
    assert "Invalid or missing API Key" in response.text


