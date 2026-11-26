"""Tests for cooling-space bookings and capacity validation."""

import pytest

from app.extensions import db
from app.centres.models import CoolingCentre
from app.bookings.models import Booking
from app.areas.models import Area
from app.residents.models import Resident
from app.requests.models import SupportRequest


@pytest.fixture
def booking_data(app):
    """Create test data for cooling space bookings"""

    #preparing db so don't need to rely on models
    area = Area(name="Bolton")
    db.session.add(area)
    db.session.commit()

    centre = CoolingCentre(
        name="Test Cooling Centre",
        location="Bolton",
        capacity=1,
        status="open",
        area_id=area.id
    )

    db.session.add(centre)
    db.session.commit()

    centre_id = centre.id
    resident = Resident(display_name="Test Resident")
    db.session.add(resident)
    db.session.commit()

    support_request = SupportRequest(
        description = "cooling_space",
        category = "cooling_space",
        resident_id = resident.id,
        area_id = area.id
    )

    db.session.add(support_request)
    db.session.commit()

    request_id = support_request.id
    return {
        "request_id": request_id,
        "centre_id": centre_id
    }

#Act
def test_book_last_available_place(client, booking_data):
    """Verifying the last available place can be booked."""

    request_id = booking_data["request_id"]
    centre_id = booking_data["centre_id"]

    response = client.post(
        "api/bookings/",
        json = {
            "request_id": request_id,
            "centre_id": centre_id
        }
    )

    #Verify
    assert response.status_code == 201, response.get_json()

    booking = Booking.query.filter_by(
        request_id = request_id,
        centre_id = centre_id
    ).one()

    assert booking.status == "pending"
    assert Booking.query.filter_by(centre_id = centre_id).count() == 1

def test_reject_booking_when_centre_is_full(client, booking_data):
    """Verify that a full cooling centre rejects further bookings."""

    centre_id = booking_data["centre_id"]
    request_id = booking_data["request_id"]

    first_response = client.post(
        "api/bookings/",
        json = {
            "request_id": request_id,
            "centre_id": centre_id
        }
    )

    #verify that booking was created sucessfully
    assert first_response.status_code == 201

    second_request = SupportRequest(
        description = "Another resident needs cooling space",
        category = "cooling_space",
        resident_id = Resident.query.first().id,
        area_id = Area.query.first().id
    )

    db.session.add(second_request)
    db.session.commit()

    second_response = client.post(
        "/api/bookings/",
        json = {
            "request_id": second_request.id,
            "centre_id": centre_id
        }
    )

    assert second_response.status_code == 409
    assert second_response.is_json
    assert Booking.query.filter_by(centre_id = centre_id).count() == 1