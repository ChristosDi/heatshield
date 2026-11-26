"""Tests for the dashboard counts of support requests.

What is tested: GET /api/reports/request-counts returns how many support requests are
outstanding, completed and rejected, and the total.

How the tests work:
- `app` and `client` come from tests/conftest.py. pytest passes them in automatically when a test
  names them as arguments. `client` sends fake HTTP requests to the API without starting a server.
- Every test gets a fresh, empty in-memory database, so tests never affect each other or your local database.
- Each test is split into three parts: Arrange (set up the data), Act (call the API), Assert (check the answer).
- All data is fictional.

Run from the api/ folder with: python -m pytest tests/test_reports.py
"""
import pytest

from app.extensions import db
# The three status groups are imported from the code itself, so the tests check the real rule.
from app.reports.service import COMPLETED, OUTSTANDING, REJECTED
from app.requests.constants import STATUSES
from app.requests.models import SupportRequest
from app.residents.models import Resident

# The address under test. Kept in one place so a change of address means one edit here.
COUNTS_URL = "/api/reports/request-counts"

# The seeded data: one fictional request is stored for each entry below.
# 2 pending + 1 in progress = 3 outstanding; 3 completed; 1 rejected; 7 in total.
SEEDED_STATUSES = ["pending", "pending", "in_progress", "completed", "completed", "completed", "rejected"]


@pytest.fixture
def seeded_requests(app):
    """Store one fictional request for each status in SEEDED_STATUSES.

    A fixture is set-up code that pytest runs before any test that names it as an argument.
    The requests are written straight to the database (not through the API), so these tests
    only depend on the counts route, not on the create-request route working.
    """
    with app.app_context():
        # Create a dummy resident to satisfy the foreign key constraint
        resident = Resident(display_name="Fictional Resident")
        db.session.add(resident)
        db.session.commit()

        for number, status in enumerate(SEEDED_STATUSES, start=1):
            db.session.add(SupportRequest(
                reference=f"REQ-{number:03d}",
                description=f"Fictional request {number}",
                category="cooling_space",
                status=status,
                resident_id=resident.id,
            ))
        db.session.commit()  # Save all 7 requests in one go.


def test_counts_are_zero_when_there_are_no_requests(client):
    """With no requests stored, every count is 0 rather than missing."""
    # Arrange: nothing to do, the database starts empty.

    # Act
    response = client.get(COUNTS_URL)

    # Assert: the call succeeds and every count is present and 0.
    # A missing count would break the dashboard, so 0 must be sent, not left out.
    assert response.status_code == 200
    assert response.get_json() == {"outstanding": 0, "completed": 0, "rejected": 0, "total": 0}


def test_counts_match_the_seeded_requests(client, seeded_requests):
    """Pending and in-progress requests count as outstanding, completed as completed,
    and rejected on its own. The three counts add up to the total."""
    # Arrange: the seeded_requests fixture has already stored the 7 requests.

    # Act
    response = client.get(COUNTS_URL)

    # Assert: the numbers match the seeded data worked out above SEEDED_STATUSES.
    assert response.get_json() == {"outstanding": 3, "completed": 3, "rejected": 1, "total": 7}


def test_counts_change_when_a_status_changes(client, app):
    """Completing a request moves it from outstanding to completed straight away."""
    with app.app_context():
        resident = Resident(display_name="Test Resident")
        db.session.add(resident)
        db.session.commit()
        resident_id = resident.id

    # Arrange: create one request through the API. New requests start as "pending", so it is outstanding.
    created = client.post("/api/requests/", json={
        # "reference": "REQ-100",
        "description": "Fictional request", 
        "category": "cooling_space",
        "resident_id": resident_id
    })
    request_id = created.get_json()["id"]
    assert client.get(COUNTS_URL).get_json()["outstanding"] == 1

    # Act: a staff member marks the request as completed.
    client.patch(f"/api/requests/id/{request_id}", json={"status": "completed"})

    # Assert: the counts are worked out on every call, never stored, so they change at once.
    counts = client.get(COUNTS_URL).get_json()
    assert counts["outstanding"] == 0
    assert counts["completed"] == 1


def test_every_status_is_counted_in_exactly_one_group():
    """Each request status belongs to exactly one count. If someone adds a new status,
    this test fails until they decide which count it belongs to."""
    # Join the three groups into one list, for example ("pending", "in_progress", "completed", "rejected").
    groups = OUTSTANDING + COMPLETED + REJECTED

    # Sorting both lists means the order does not matter. If a status is missing from the groups,
    # or sits in two groups, the lists differ and the test fails. Without this check, a new
    # status would silently be left out of every count on the dashboard.
    assert sorted(groups) == sorted(STATUSES)


def test_counts_cannot_be_changed_through_the_api(client):
    """The counts are read-only: sending data to the address is refused with 405 in the usual JSON error format."""
    # Act: try to overwrite the counts with a POST.
    response = client.post(COUNTS_URL, json={"outstanding": 100})

    # Assert: 405 means "Method Not Allowed": the address exists but only accepts GET.
    # is_json checks the error comes back as JSON, like every other API error.
    assert response.status_code == 405
    assert response.is_json