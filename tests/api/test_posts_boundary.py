"""
Playwright API Test Suite: JSONPlaceholder POST Boundary & Resilience Testing
Endpoint: POST https://jsonplaceholder.typicode.com/posts

Objectives:
Validate the API's handling of boundary, edge-case, and invalid data during post creation:
1. Excessively long strings for titles (e.g., 5,000, 20,000, 50,000 characters).
2. Unsupported special characters, SQL injection, XSS vectors, and Unicode boundaries.
3. Missing required fields (missing userId, missing title, missing body, empty JSON object).
4. Boundary data types (negative userId, string userId, extreme integer overflows).
5. Ensure server-side resilience: No 500 Internal Server Errors, graceful handling.
"""

import pytest
import json
from playwright.sync_api import Playwright, APIRequestContext

BASE_API_URL = "https://jsonplaceholder.typicode.com"
POSTS_ENDPOINT = f"{BASE_API_URL}/posts"


@pytest.fixture(scope="session")
def api_context(playwright: Playwright) -> APIRequestContext:
    """Creates a shared Playwright APIRequestContext configured for JSONPlaceholder."""
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "Accept": "application/json",
        "User-Agent": "Streamhub-Playwright-Resilience-Testing-Suite/1.0",
    }
    request_context = playwright.request.new_context(
        base_url=BASE_API_URL,
        extra_http_headers=headers,
        timeout=30000,
    )
    yield request_context
    request_context.dispose()


class TestPostsBoundaryApi:
    """Test Suite validating POST /posts under boundary conditions and invalid inputs."""

    def test_post_creation_baseline_valid_payload(self, api_context: APIRequestContext):
        """Baseline test: standard post creation returns 201 Created with valid id."""
        payload = {
            "title": "Streamhub Automated Quality Engineering",
            "body": "Validating robust API behavior and contract integrity.",
            "userId": 1,
        }

        response = api_context.post("/posts", data=payload)
        status_code = response.status
        data = response.json()

        print(f"\n[Baseline Test] Status: {status_code}, Response Body: {data}")
        assert status_code in (200, 201), f"Expected 200/201 but got {status_code}"
        assert data.get("id") == 101, f"Expected mock ID 101, got {data.get('id')}"
        assert data.get("title") == payload["title"]
        assert data.get("userId") == payload["userId"]

    @pytest.mark.parametrize(
        "char_count, description",
        [
            (5000, "5KB title string"),
            (25000, "25KB title string"),
            (50000, "50KB boundary title string"),
        ],
    )
    def test_excessively_long_strings_in_title(
        self, api_context: APIRequestContext, char_count: int, description: str
    ):
        """
        Scenario 1: Send excessively long strings for titles.
        Verifies API resilience: does not trigger 500 Internal Server Error,
        handles payload boundaries gracefully.
        """
        oversized_title = "A" * char_count
        payload = {
            "title": oversized_title,
            "body": "Testing large payload buffer management.",
            "userId": 42,
        }

        response = api_context.post("/posts", data=payload)
        status_code = response.status

        print(f"\n[Boundary: {description}] Status: {status_code}, Length Sent: {len(oversized_title)}")

        # Crucial resilience assertion: Server must NOT throw a 5xx Internal Server Error
        assert status_code < 500, f"Server crashed with 5xx error! Status: {status_code}"

        # Production contract vs mock:
        # Strict APIs return 413 (Payload Too Large) or 400 (Bad Request).
        # JSONPlaceholder mock accepts and echoes with 201.
        assert status_code in (201, 400, 413, 422), f"Unexpected status code {status_code}"

        if status_code in (200, 201):
            data = response.json()
            assert data.get("id") is not None
            assert len(data.get("title", "")) == char_count

    @pytest.mark.parametrize(
        "payload_type, special_payload",
        [
            ("XSS_Script_Injection", "<script>alert('STREAMHUB_SEC_AUDIT')</script><img src=x onerror=alert(1)>"),
            ("SQL_Injection_Payload", "'; DROP TABLE posts; SELECT * FROM users WHERE '1'='1'--"),
            ("Unicode_Surrogate_Emojis", "🔥✨🚀🛡️💯 𝕽𝖊𝖘𝖎𝖑𝖎𝖊𝖓𝖈𝖊 測試 テスト اختبار"),
            ("RTL_Control_Characters", "\u202E\u200F\u202BReverseTextDirection\u200E\u202C"),
            ("Null_Byte_Injection", "prefix_text\x00suffix_hidden_payload"),
        ],
    )
    def test_unsupported_special_characters_and_security_payloads(
        self, api_context: APIRequestContext, payload_type: str, special_payload: str
    ):
        """
        Scenario 2: Send unsupported special characters, injection patterns, and Unicode.
        Verifies API resilience against code injection, memory corruption, and character encoding faults.
        """
        payload = {
            "title": f"Test {payload_type}: {special_payload}",
            "body": f"Boundary content with {special_payload}",
            "userId": 7,
        }

        response = api_context.post("/posts", data=payload)
        status_code = response.status

        print(f"\n[Special Chars: {payload_type}] Status: {status_code}")

        # Resilience assertion: API must NOT crash (no 500 / 502 / 503)
        assert status_code < 500, f"API encountered server-side failure {status_code} for {payload_type}"
        assert status_code in (200, 201, 400, 422), f"Unexpected HTTP status code: {status_code}"

        if status_code in (200, 201):
            data = response.json()
            assert data.get("id") is not None
            # Verify data integrity preserved without corruption
            assert payload["title"] in data.get("title", "")

    @pytest.mark.parametrize(
        "case_name, payload",
        [
            ("Missing_UserId", {"title": "Post Without User ID", "body": "Body content"}),
            ("Missing_Title", {"body": "Post Without Title", "userId": 1}),
            ("Missing_Body", {"title": "Post Without Body", "userId": 1}),
            ("Empty_JSON_Object", {}),
            ("Null_Fields", {"title": None, "body": None, "userId": None}),
        ],
    )
    def test_missing_required_fields(
        self, api_context: APIRequestContext, case_name: str, payload: dict
    ):
        """
        Scenario 3: Send POST request missing required fields (e.g. userId, title, body, empty object).
        Verifies API handles absent fields cleanly without unhandled server exceptions.
        """
        response = api_context.post("/posts", data=payload)
        status_code = response.status

        print(f"\n[Missing Field: {case_name}] Status: {status_code}")

        # Server must not fail with 500
        assert status_code < 500, f"Server failed with {status_code} on {case_name}"

        # Production contract expectation:
        # A strictly validated production API requires userId and title, returning 400/422.
        # JSONPlaceholder mock API responds with 201.
        assert status_code in (200, 201, 400, 422), f"Unexpected status code: {status_code}"

        if status_code in (200, 201):
            data = response.json()
            assert "id" in data, f"Response should still return an identifier or error object: {data}"

    @pytest.mark.parametrize(
        "case_name, invalid_userId",
        [
            ("String_UserId", "streamhub_invalid_user"),
            ("Negative_UserId", -9999),
            ("Extreme_Large_UserId", 9999999999999999),
            ("Float_UserId", 3.14159),
        ],
    )
    def test_invalid_and_boundary_field_data_types(
        self, api_context: APIRequestContext, case_name: str, invalid_userId
    ):
        """
        Scenario 4: Send non-integer, negative, or overflow values for userId.
        Verifies data type validation resilience and error boundary handling.
        """
        payload = {
            "title": f"Testing invalid data type for userId ({case_name})",
            "body": "Evaluating schema type-coercion and validation constraints.",
            "userId": invalid_userId,
        }

        response = api_context.post("/posts", data=payload)
        status_code = response.status

        print(f"\n[Invalid Type: {case_name}] Status: {status_code}")

        # API must maintain server stability
        assert status_code < 500, f"API crashed on invalid userId type: {status_code}"
        assert status_code in (200, 201, 400, 422), f"Unexpected response status {status_code}"
