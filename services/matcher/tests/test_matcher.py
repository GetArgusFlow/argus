# argus/services/matcher/tests/test_matcher.py

import pytest
import httpx
import json
import time
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8004/api/v1"
TEST_CASES_DIR = Path(__file__).parent / "test_cases"

# ADD API KEY FOR TESTING
# This uses the default key from config.py
DEV_API_KEY = "default_dev_key"
HEADERS = {"x-api-key": DEV_API_KEY}
#

# Details for the temporary product
TEST_PRODUCT_ID = 999
TEST_PRODUCT_TITLE = "My Pytest Product (Coca)"

# Helper Function

def search_for_text(query: str) -> list[int]:
    """Helper function to search and return a list of IDs."""
    try:
        r = httpx.post(
            f"{BASE_URL}/match/text", 
            json={"text": query, "top_k": 5}, 
            timeout=10.0,
            headers=HEADERS
        )
        r.raise_for_status()
        matches = r.json().get("matches", [])
        return [match[0] for match in matches] 
    except Exception as e:
        pytest.fail(f"Search query '{query}' failed: {e}")

# Test for /match/text

def find_test_cases():
    """Finds all subdirectories in the test_cases directory."""
    if not TEST_CASES_DIR.is_dir():
        return []
    return [d for d in TEST_CASES_DIR.iterdir() if d.is_dir()]

def test_matcher_with_case(test_case_dir: Path):
    input_json_path = test_case_dir / "input.json"
    expected_json_path = test_case_dir / "expected_output.json"
    assert input_json_path.exists()
    assert expected_json_path.exists()

    with open(input_json_path, 'r', encoding='utf-8') as f:
        payload = json.load(f)

    with open(expected_json_path, 'r', encoding='utf-8') as f:
        expected_output = json.load(f)

    try:
        # Route now requires key, so add headers=HEADERS
        response = httpx.post(
            f"{BASE_URL}/match/text", 
            json=payload, 
            timeout=30.0, 
            headers=HEADERS
        )
        response.raise_for_status()
    except httpx.RequestError as e:
        pytest.fail(f"Request failed for test case '{test_case_dir.name}': {e}")

    actual_output = response.json()
    actual_ids = [match[0] for match in actual_output.get("matches", [])]
    expected_ids = [match[0] for match in expected_output.get("matches", [])]

    print(f"\nTest Case: {test_case_dir.name}")
    print(f"  Input: {payload}")
    print(f"  Expected IDs: {expected_ids}")
    print(f"  Actual IDs: {actual_ids}")

    assert actual_ids == expected_ids, \
        f"Output for '{test_case_dir.name}' did not return the correct product IDs in the correct order."
    
    print(f"Test Passed: {test_case_dir.name}")


def pytest_generate_tests(metafunc):
    """
This is the pytest hook for dynamic parametrization.
"""
    if "test_case_dir" in metafunc.fixturenames:
        test_cases = find_test_cases()
        ids = [case.name for case in test_cases]
        metafunc.parametrize("test_case_dir", test_cases, ids=ids)


# Test for Add/Delete Cycle

def test_add_delete_product_cycle():
    """
    Tests the full add/delete cycle using the new test endpoints.
    This test uses the 'search_for_text' helper, which is now fixed.
    """
    
    add_payload = {
        "product_id": TEST_PRODUCT_ID,
        "store_id": 1,
        "title": TEST_PRODUCT_TITLE
    }
    
    try:
        # 1. VERIFY IT DOESN'T EXIST (Uses secured helper)
        print(f"Verifying product {TEST_PRODUCT_ID} is not in index (pre-check)...")
        ids_before = search_for_text(TEST_PRODUCT_TITLE)
        assert TEST_PRODUCT_ID not in ids_before, "Product should not be in the index before adding"

        # 2. ADD THE TEST PRODUCT (Protected test route)
        print(f"Calling API to add test product {TEST_PRODUCT_ID}...")
        r_add = httpx.post(
            f"{BASE_URL}/admin/test/add_product", 
            json=add_payload, 
            headers=HEADERS
        )
        r_add.raise_for_status()
        assert r_add.json() == {"status": "added_test_product", "product_id": TEST_PRODUCT_ID}

        time.sleep(0.1) 

        # 3. VERIFY ADD (Uses secured helper)
        print(f"Verifying product {TEST_PRODUCT_ID} was added...")
        ids_after_add = search_for_text(TEST_PRODUCT_TITLE)
        assert TEST_PRODUCT_ID in ids_after_add, "Product was not found in index after add"
        assert ids_after_add[0] == TEST_PRODUCT_ID, "Test product should be the #1 match"
        print("Verify add... PASSED")

    finally:
        # 4. CLEANUP (Protected test route)
        print(f"\nCleaning up test product {TEST_PRODUCT_ID}...")
        del_payload = {"product_id": TEST_PRODUCT_ID}
        r_del = httpx.post(
            f"{BASE_URL}/admin/test/delete_product", 
            json=del_payload, 
            headers=HEADERS
        )
        
        if r_del.status_code == 200:
            assert r_del.json() == {"status": "deleted_test_product", "product_id": TEST_PRODUCT_ID}
            print(f"Successfully deleted {TEST_PRODUCT_ID} from DB and index.")
        else:
            print(f"Cleanup failed with status {r_del.status_code}: {r_del.text}")

    # 5. VERIFY DELETE (Uses secured helper)
    print(f"Verifying product {TEST_PRODUCT_ID} was deleted...")
    ids_after_delete = search_for_text(TEST_PRODUCT_TITLE)
    assert TEST_PRODUCT_ID not in ids_after_delete, "Product was still found after deletion"
    print("Verify delete... PASSED")
    print("Test Passed: Add/Delete cycle complete.")

# Test for Security

# A list of all protected endpoints (method, path, sample_json_payload)
# We will test all of them
PROTECTED_ENDPOINTS_TO_TEST = [
    ("POST", "/match/text", {"text": "test"}),
    ("POST", "/match/id", {"product_id": 1}),
    ("POST", "/update/product", {"product_id": 1}),
    ("POST", "/delete/product", {"product_id": 1}),
    ("POST", "/admin/train", None),
    ("POST", "/admin/retrain", None),
    ("POST", "/admin/test/add_product", {"product_id": 999, "store_id": 1, "title": "test"}),
    ("POST", "/admin/test/delete_product", {"product_id": 999}),
]

# A list of "bad" authentication configurations to test
BAD_AUTH_CONFIGS = [
    # Test with no 'x-api-key' header at all
    pytest.param({}, id="no_key_provided"),
    
    # Test with an invalid 'x-api-key' header
    pytest.param({"x-api-key": "this-is-the-wrong-key"}, id="wrong_key_provided")
]

@pytest.mark.parametrize("headers", BAD_AUTH_CONFIGS)
@pytest.mark.parametrize("method, path, json_payload", PROTECTED_ENDPOINTS_TO_TEST)
def test_protected_routes_fail_with_bad_auth(method, path, json_payload, headers):
    """
    Tests that all protected routes fail with 401 if the API key is missing or wrong.
    This test confirms the [Depends(get_api_key)] security is working.
    """
    url = f"{BASE_URL}{path}"
    
    # We use a client to make a request with a custom method and headers
    client = httpx.Client()
    
    request_args = {
        "method": method,
        "url": url,
        "headers": headers
    }
    # Add JSON payload only if one is required
    if json_payload:
        request_args["json"] = json_payload
        
    response = client.request(**request_args)
    
    # We MUST get a 401 Unauthorized error
    assert response.status_code == 401, f"Expected 401 for {path} with {headers}, got {response.status_code}"
    
    # Check that the error message is correct
    assert "Invalid or missing API Key" in response.text