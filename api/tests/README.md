# HeatShield API Testing Documentation

## 1. Purpose

The purpose of the HeatShield API test suite is to verify that all Flask API endpoints behave correctly before they are used by the frontend application or other dependent services.

The tests verify that:

- Valid requests are processed successfully.
- Invalid requests are rejected appropriately.
- Required fields are validated.
- Invalid values are rejected.
- API responses contain the expected JSON data.
- Correct HTTP status codes are returned.
- Missing resources produce appropriate JSON error responses.
- Database operations behave as expected.

The test suite supports the development team's requirement for reliable, repeatable and automated API testing.

## 2. Testing Framework

The project uses **pytest** as its testing framework.

Flask's built-in test client is used to send HTTP requests directly to the application without running an external web server.

This approach allows endpoints to be tested using realistic HTTP methods and request data while keeping the tests isolated from external services.

### Main testing tools

| Tool | Purpose |
| --- | --- |
| pytest | Test execution and assertions |
| Flask test client | Simulate HTTP requests |
| Flask application factory | Create isolated application instances |
| SQLAlchemy | Manage the test database |
| Mock adapter | Replace external AI integrations |

## 3. API Endpoints Under Test

The following support request endpoints are currently covered by the test suite.

### 3.1 Create support request

**Endpoint:** `POST /api/requests/`

Purpose: Create a new support request.

Valid request example:

```json
{
  "description": "Resident needs a cooling space",
  "category": "cooling_space",
  "area": "Bolton"
}
```

Expected response:

- HTTP 201 Created.
- JSON response containing the newly created request.
- Automatically assigned request ID.
- Default status of `pending`.

Invalid scenarios:

- Missing description.
- Invalid category.
- Empty description.
- Description exceeding the maximum length.

Expected response: HTTP 400 Bad Request with a JSON validation error.

### 3.2 Retrieve all support requests

**Endpoint:** `GET /api/requests/`

Purpose: Retrieve all support requests, optionally applying filters.

Supported query parameters:

| Parameter | Description |
| --- | --- |
| category | Filter by request category |
| status | Filter by request status |
| priority | Filter by priority |
| area | Filter by area |

Expected response:

- HTTP 200 OK.
- JSON array containing matching requests.

Invalid scenarios:

- Unsupported category.
- Unsupported status.
- Unsupported priority.

Expected response: HTTP 400 Bad Request with a JSON validation error.

### 3.3 Retrieve an individual support request

**Endpoint:** `GET /api/requests/{request_id}`

Purpose: Retrieve a specific support request using its unique identifier.

Valid scenario:

- Request an existing support request ID.

Expected response:

- HTTP 200 OK.
- JSON object containing the requested support request.

Invalid scenario:

- Request an ID that does not exist.

Expected response:

- HTTP 404 Not Found.
- JSON error message indicating that the request was not found.

### 3.4 Update a support request

**Endpoint:** `PATCH /api/requests/{request_id}`

Purpose: Update selected fields of an existing support request.

Valid request example:

```json
{
  "status": "in_progress",
  "priority": "high"
}
```

Expected response:

- HTTP 200 OK.
- JSON object containing the updated support request.

Invalid scenarios:

- Invalid priority.
- Invalid status.
- Description outside the permitted length.
- Request ID does not exist.

Expected responses:

- HTTP 400 Bad Request for invalid input.
- HTTP 404 Not Found for an unknown request.

### 3.5 Delete a support request

**Endpoint:** `DELETE /api/requests/{request_id}`

Purpose: Delete an existing support request.

Valid scenario:

- Delete an existing support request.

Expected response:

- HTTP 204 No Content.

The test then attempts to retrieve the deleted request to verify that it no longer exists.

Invalid scenario:

- Attempt to delete a request that does not exist.

Expected response:

- HTTP 404 Not Found.
- JSON error message.

## 4. Test Cases

The current support request test suite includes the following scenarios:

| Test | Description | Expected result |
| --- | --- | --- |
| test_create_request | Create a valid request | 201 |
| test_create_request_invalid_category | Reject invalid category | 400 |
| test_create_request_missing_description | Reject missing description | 400 |
| test_get_all_requests | Retrieve all requests | 200 |
| test_get_single_request | Retrieve an existing request | 200 |
| test_get_unknown_request | Retrieve an unknown request | 404 |
| test_update_request | Update an existing request | 200 |
| test_update_request_invalid_priority | Reject invalid priority | 400 |
| test_update_unknown_request | Update an unknown request | 404 |
| test_delete_request | Delete an existing request | 204 |
| test_delete_unknown_request | Delete an unknown request | 404 |
| test_filter_requests | Filter requests | 200 |

## 5. Database Isolation and Test Data

All API tests should use a dedicated test database.

The test database must be separate from development and production databases.

The application factory allows tests to provide a separate configuration through `test_config`.

The test setup should:

1. Create a fresh test application.
2. Configure an isolated SQLite test database.
3. Initialise the database tables.
4. Insert fictional test data when required.
5. Provide the Flask test client.
6. Clean up the database after execution.

Fictional data should be used throughout the test suite. Tests must not rely on real resident information or production records.

## 6. External Services and AI Integrations

Tests must not require external network access or real AI API credentials.

Any AI functionality should be accessed through the project's mock adapter during testing.

The mock adapter should return predictable responses so tests can verify application behaviour without contacting external AI services.

This ensures that test execution is:

- Independent of external services.
- Consistent across development environments.
- Free from unexpected API costs.
- Suitable for automated CI/CD pipelines.

## 7. Running the Tests

From the project root directory:


```bash
pytest
```

Run with detailed test names:

```bash
pytest -v
```

Run a specific test module:

```bash
pytest tests/requests/test_routes.py -v
```

All tests should pass before changes are submitted for review.

## 8. Expected Error Response Format

Invalid requests and missing resources should return structured JSON errors.

For example:


```json
{
  "code": 400,
  "message": "Bad Request",
  "errors": {
    "json": {
      "category": [
        "Must be one of: cooling_space, welfare_visit, practical_assistance."
      ]
    }
  }
}
```

The exact error structure depends on the application's registered Flask-Smorest and custom error handlers.

Tests should verify the actual agreed response format rather than assuming every error has the same structure.

Successful DELETE requests return HTTP 204 and therefore do not require a JSON response body.

## 9. Maintaining the Test Suite

Whenever a new API endpoint is introduced or an existing endpoint is modified, corresponding tests must be included in the same pull request.

Each endpoint should have tests covering:

- At least one valid request.
- At least one invalid request.
- Expected HTTP status codes.
- Expected JSON response data.
- Validation and error handling.
- Relevant database behaviour.

The complete test suite must pass before changes are merged into the main branch.

## 10. Definition of Done

API testing is considered complete when:

- Every Flask API route has valid and invalid request tests.
- HTTP status codes are verified.
- Successful JSON responses are verified.
- JSON error responses are verified.
- Tests use an isolated test database.
- Fictional test data is used.
- AI integrations use the mock adapter.
- Tests require no external network access or real AI credentials.
- All tests run through one documented command.
- The README documents the endpoints covered.
- Changes are reviewed and merged into the main branch.
