"""Tests for US05a: filtering support requests."""

import itertools

import pytest
from app.areas.models import Area
from app.extensions import db
from app.residents.models import Resident

# Notice we are using the new DB field names and FK references
TEST_REQUESTS = [
    {
        # "reference": "REQ-001",
        "description": "Resident needs a cooling space",
        "category": "cooling_space",
        "status": "pending",
        "operational_priority": "high",
        "area_name": "Bolton",
    },
    {
        # "reference": "REQ-002",
        "description": "Resident needs a welfare visit",
        "category": "welfare_visit",
        "status": "in_progress",
        "operational_priority": "normal",
        "area_name": "Farnworth",
    },
    {
        # "reference": "REQ-003",
        "description": "Resident needs practical assistance",
        "category": "practical_assistance",
        "status": "completed",
        "operational_priority": "low",
        "area_name": "Bolton",
    },
]


@pytest.fixture
def sample_requests(client, app):
    """Create three requests and their relational data through the API."""
    created_data = []

    with app.app_context():
        # 1. Create the distinct areas
        bolton = Area(name="Bolton")
        farnworth = Area(name="Farnworth")
        db.session.add_all([bolton, farnworth])

        # 2. Create a test resident
        resident = Resident(display_name="Test Resident")
        db.session.add(resident)
        db.session.commit()

        area_map = {"Bolton": bolton.id, "Farnworth": farnworth.id}
        resident_id = resident.id

    # 3. Create the requests via the API
    for req_data in TEST_REQUESTS:
        payload = {
            # "reference": req_data["reference"],
            "description": req_data["description"],
            "category": req_data["category"],
            "status": req_data["status"],
            "operational_priority": req_data["operational_priority"],
            "resident_id": resident_id,
            "area_id": area_map[req_data["area_name"]],
        }

        response = client.post("/api/requests/", json=payload)
        assert response.status_code == 201

        # Keep track of the IDs for the filtering logic later
        req_data["area_id"] = area_map[req_data["area_name"]]
        created_data.append(req_data)

    return created_data


@pytest.mark.parametrize(
    "field,value,expected_count",
    [
        ("category", "cooling_space", 1),
        ("status", "pending", 1),
        ("operational_priority", "high", 1),
        # We filter by area ID, not the name
        ("area_id", 1, 2),
    ],
)
def test_filter_by_single_field(client, sample_requests, field, value, expected_count):
    """Each supported field filters requests correctly."""
    response = client.get(
        "/api/requests/",
        query_string={field: value},
    )

    assert response.status_code == 200
    results = response.get_json()
    assert len(results) == expected_count
    assert all(item[field] == value for item in results)


FILTER_FIELDS = ["category", "status", "operational_priority", "area_id"]

# Manually define the values for the FIRST test request
# (Bolton is area_id 1 in our fixture)
FIRST_REQUEST_VALUES = {
    "category": "cooling_space",
    "status": "pending",
    "operational_priority": "high",
    "area_id": 1,
}

FILTER_COMBINATIONS = [
    dict(zip(fields, values))
    for size in range(2, len(FILTER_FIELDS) + 1)
    for fields in itertools.combinations(FILTER_FIELDS, size)
    for values in [tuple(FIRST_REQUEST_VALUES[field] for field in fields)]
]


@pytest.mark.parametrize("filters", FILTER_COMBINATIONS)
def test_filter_by_multiple_fields(client, sample_requests, filters):
    """All combinations of two or more filters return correct results."""
    response = client.get("/api/requests/", query_string=filters)

    assert response.status_code == 200
    results = response.get_json()

    assert len(results) == 1
    assert all(
        all(item[field] == value for field, value in filters.items())
        for item in results
    )


def test_filter_with_no_matches(client, sample_requests):
    """Return an empty list when no requests match."""
    response = client.get(
        "/api/requests/",
        query_string={
            "category": "cooling_space",
            "status": "completed",
        },
    )

    assert response.status_code == 200
    assert response.get_json() == []


def test_filter_with_no_parameters(client, sample_requests):
    """Return all requests when no filters are supplied."""
    response = client.get("/api/requests/")

    assert response.status_code == 200
    assert len(response.get_json()) == 3


def test_filter_by_area_id(client, sample_requests):
    """Test filtering explicitly by area_id returns the correct count."""
    # Bolton is area_id 1 in our fixture, and has 2 requests
    response = client.get(
        "/api/requests/",
        query_string={"area_id": 1},
    )

    assert response.status_code == 200
    assert len(response.get_json()) == 2


@pytest.mark.parametrize(
    "field,value",
    [
        ("category", "invalid_category"),
        ("status", "invalid_status"),
        ("operational_priority", "invalid_priority"),
        ("area_id", "not-an-integer"),  # Schema expects int now
    ],
)
def test_invalid_filter_value_returns_400(client, sample_requests, field, value):
    """Invalid filtering values should return HTTP 400."""
    response = client.get(
        "/api/requests/",
        query_string={field: value},
    )

    assert response.status_code == 400
