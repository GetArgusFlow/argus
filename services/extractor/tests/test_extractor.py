# extractor/tests/test_extractor.py

import pytest
import httpx
import json
from pathlib import Path
from deepdiff import DeepDiff

# Configuration
SERVICE_URL = "http://localhost:8001/api/v1/extract"
TEST_CASES_DIR = Path(__file__).parent / "test_cases"
DEV_API_KEY = "default_dev_key"
HEADERS = {"x-api-key": DEV_API_KEY}

def find_test_cases():
    """Finds all subdirectories in the test_cases directory."""
    if not TEST_CASES_DIR.is_dir():
        return []
    return [d for d in TEST_CASES_DIR.iterdir() if d.is_dir()]

def test_extractor_with_case(test_case_dir: Path):
    """
    A data-driven test that runs for each test case directory.
    Pytest will call this function once for every folder found.
    """
    input_html_path = test_case_dir / "input.html"
    expected_json_path = test_case_dir / "expected_output.json"

    assert input_html_path.exists(), f"Missing input.html in {test_case_dir.name}"
    assert expected_json_path.exists(), f"Missing expected_output.json in {test_case_dir.name}"

    html_content = input_html_path.read_text(encoding='utf-8')
    with open(expected_json_path, 'r', encoding='utf-8') as f:
        expected_output = json.load(f)

    payload = {
        "html_content": html_content,
        "url": f"http://example.com/{test_case_dir.name}"
    }

    try:
        response = httpx.post(SERVICE_URL, json=payload, timeout=30.0, headers=HEADERS)
        response.raise_for_status()
    except httpx.RequestError as e:
        pytest.fail(f"Request failed for test case '{test_case_dir.name}': {e}")

    actual_result = response.json()
    actual_data = actual_result.get("data")

    if actual_data:
        # Remove volatile fields that we don't want to compare
        actual_data.pop('field_status', None)
        actual_data.pop('selectors_used', None)

    print(f"\nExpected (subset) result:\n{expected_output}")
    print(f"\nActual (superset) result:\n{actual_data}")

    # Compare the actual result (superset) against the expected result (subset).
    # 'dictionary_item_removed' = keys in 'actual' but not in 'expected' (This is OK)
    # 'iterable_item_removed' = items in lists in 'actual' but not in 'expected' (This is OK)
    diff = DeepDiff(actual_data, expected_output, ignore_order=True)

    # Create a copy of the diff to check for unacceptable differences.
    # We will remove the "acceptable" differences from this copy.
    diff_to_check = diff.copy()

    # It's OK if the 'actual' result has extra keys.
    diff_to_check.pop('dictionary_item_removed', None)
    
    # It's OK if the 'actual' result has extra items in its lists.
    diff_to_check.pop('iterable_item_removed', None)

    # The test should fail if any *other* differences remain, such as:
    # - 'values_changed' (data mismatch)
    # - 'dictionary_item_added' (data from 'expected' is missing in 'actual')
    # - 'type_changes' (data types mismatch)
    assert not diff_to_check, f"Output for '{test_case_dir.name}' did not match expected subset:\n{diff.pretty()}"
    
    print(f"\nTest Passed: {test_case_dir.name}")


def pytest_generate_tests(metafunc):
    """
    This is the pytest hook for dynamic parametrization.
    It finds the 'test_case_dir' parameter in test functions and injects
    the test cases found on the filesystem.
    """
    if "test_case_dir" in metafunc.fixturenames:
        test_cases = find_test_cases()

        ids = [case.name for case in test_cases]
        metafunc.parametrize("test_case_dir", test_cases, ids=ids)

@pytest.mark.parametrize("headers", [
    pytest.param({}, id="no_key_provided"),
    pytest.param({"x-api-key": "this-is-the-wrong-key"}, id="wrong_key_provided")
])
def test_extract_fails_with_bad_auth(headers):
    """
    Tests that the /extract endpoint fails with 401 if auth is missing or wrong.
    """
    payload = {
        "url": "http://example.com",
        "html_content": "<html></html>"
    }
    
    response = httpx.post(SERVICE_URL, json=payload, headers=headers)
    
    # We MUST get a 401 Unauthorized error
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    # Check that the error message is correct
    assert "Invalid or missing API Key" in response.text