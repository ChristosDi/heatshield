
"""Tests for US05a: filtering support requests."""

import itertools

import pytest


TEST_REQUESTS = [
    {
        "description": "Resident needs a cooling space",
        "category": "cooling_space",
        "status": "pending",
        "priority": "high",
        "area": "Bolton",
    },
    {
        "description": "Resident needs a welfare visit",
        "category": "welfare_visit",
        "status": "in_progress",
        "priority": "normal",
        "area": "Farnworth",
    },
    {
        "description": "Resident needs practical assistance",
        "category": "practical_assistance",
        "status": "completed",
        "priority": "low",
        "area": "Bolton",
    },
]


@pytest.fixture
def sample_requests(client):
    """Create three requests through the existing API."""
    for request_data in TEST_REQUESTS:
        response = client.post("/api/requests/", json=request_data)
        assert response.status_code == 201

    return TEST_REQUESTS


@pytest.mark.parametrize(
    "field,value,expected_count",
    [
        ("category", "cooling_space", 1),
        ("status", "pending", 1),
        ("priority", "high", 1),
        ("area", "Bolton", 2),
    ],
)
def test_filter_by_single_field(
    client, sample_requests, field, value, expected_count
):
    """Each supported field filters requests correctly."""
    response = client.get(
        "/api/requests/",
        query_string={field: value},
    )

    assert response.status_code == 200
    results = response.get_json()
    assert len(results) == expected_count
    assert all(item[field] == value for item in results)


FILTER_FIELDS = ["category", "status", "priority", "area"]

FILTER_COMBINATIONS = [
    dict(zip(fields, values))
    for size in range(2, len(FILTER_FIELDS) + 1)
    for fields in itertools.combinations(FILTER_FIELDS, size)
    for values in [
        tuple(TEST_REQUESTS[0][field] for field in fields)
    ]
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


def test_filter_invalid_area_type(client, sample_requests):
    """An area name is a string, not a numeric identifier."""
    response = client.get(
        "/api/requests/",
        query_string={"area": "Bolton"},
    )

    assert response.status_code == 200
    assert len(response.get_json()) == 2


@pytest.mark.parametrize(
    "field,value",
    [
        ("category", "invalid_category"),
        ("status", "invalid_status"),
        ("priority", "invalid_priority"),
    ],
)
def test_invalid_filter_value_returns_400(
    client, sample_requests, field, value
):
    """Invalid filtering values should return HTTP 400."""
    response = client.get(
        "/api/requests/",
        query_string={field: value},
    )

    assert response.status_code == 400
