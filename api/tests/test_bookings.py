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

def test_reject_booking_when_centre_is_closed(client, booking_data):
    """Verify that a closed cooling centre rejects bookings."""

    # Arrange
    centre_id = booking_data["centre_id"]
    request_id = booking_data["request_id"]

    centre = db.session.get(CoolingCentre, centre_id)
    centre.status = "closed"
    db.session.commit()

    # Act - try make a booking
    response = client.post(
        "api/bookings/",
        json = {
            "request_id": request_id,
            "centre_id": centre_id
        }
    )

    # Assert
    assert response.status_code == 409
    assert response.is_json
    assert Booking.query.filter_by(centre_id = centre_id).count() == 0

def test_reassign_booking_to_available_centre(client, booking_data):
    """Verify that an existing booking can move to an available centre."""

    # Arrange
    original_centre_id = booking_data["centre_id"]

    original_centre = db.session.get(
        CoolingCentre,
        original_centre_id
    )

    new_centre = CoolingCentre(
        name="Second Cooling Centre",
        location="Bolton",
        capacity=1,
        status="open",
        area_id=original_centre.area_id
    )

    db.session.add(new_centre)
    db.session.commit()

    new_centre_id = new_centre.id

    create_response = client.post(
        "/api/bookings/",
        json=booking_data
    )

    assert create_response.status_code == 201

    booking_id = create_response.get_json()["id"]

    # Act - reassign the existing booking.
    response = client.patch(
        f"/api/bookings/{booking_id}",
        json={"centre_id": new_centre_id}
    )

    # Assert
    assert response.status_code == 200, response.get_json()
    assert response.is_json

    db.session.expire_all()

    booking = db.session.get(Booking, booking_id)

    assert booking.centre_id == new_centre_id
    assert booking.request_id == booking_data["request_id"]
    assert booking.status == "pending"

    # Verify that the original place has been released.
    assert Booking.query.filter_by(
        centre_id=original_centre_id
    ).count() == 0

    # Verify that the destination place is occupied.
    assert Booking.query.filter_by(
        centre_id=new_centre_id
    ).count() == 1

    # Verify that no duplicate booking was created.
    assert Booking.query.count() == 1

@pytest.mark.parametrize("destination_status, capacity", [
    ("open", 1),
    ("closed", 1)
])
def test_reject_reassignment_to_unavailable_centre(
    client, booking_data, destination_status, capacity
):
    """Verify that reassignment to a full or closed centre is rejected."""

    # Arrange
    original_centre_id = booking_data["centre_id"]
    original_centre = db.session.get(
        CoolingCentre,
        original_centre_id
    )

    destination = CoolingCentre(
        name="Destination Cooling Centre",
        location="Bolton",
        capacity=capacity,
        status=destination_status,
        area_id=original_centre.area_id
    )

    db.session.add(destination)
    db.session.commit()

    destination_id = destination.id

    create_response = client.post(
        "/api/bookings/",
        json=booking_data
    )

    assert create_response.status_code == 201
    booking_id = create_response.get_json()["id"]

    # Fill the destination centre when it is open.
    if destination_status == "open":
        second_request = SupportRequest(
            description="Another resident needs cooling space",
            category="cooling_space",
            resident_id=Resident.query.first().id,
            area_id=original_centre.area_id
        )

        db.session.add(second_request)
        db.session.commit()

        fill_response = client.post(
            "/api/bookings/",
            json={
                "request_id": second_request.id,
                "centre_id": destination_id
            }
        )

        assert fill_response.status_code == 201

    original_count = Booking.query.count()

    # Act
    response = client.patch(
        f"/api/bookings/{booking_id}",
        json={"centre_id": destination_id}
    )

    # Assert
    assert response.status_code == 409, response.get_json()
    assert response.is_json

    db.session.expire_all()

    booking = db.session.get(Booking, booking_id)

    assert booking.centre_id == original_centre_id
    assert booking.status == "pending"
    assert booking.request_id == booking_data["request_id"]
    assert Booking.query.count() == original_count

    expected_count = 1 if destination_status == "open" else 0

    assert Booking.query.filter_by(
        centre_id=destination_id
    ).count() == expected_count

def test_update_booking_at_full_centre(client, booking_data):
    """Verify that an existing booking does not count its own place twice."""

    # Arrange
    create_response = client.post(
        "/api/bookings/",
        json=booking_data
    )

    assert create_response.status_code == 201

    booking_id = create_response.get_json()["id"]

    # Act - approve the existing booking.
    response = client.patch(
        f"/api/bookings/{booking_id}",
        json={"status": "approved"}
    )

    # Assert
    assert response.status_code == 200, response.get_json()

    db.session.expire_all()

    booking = db.session.get(Booking, booking_id)

    assert booking.status == "approved"
    assert booking.centre_id == booking_data["centre_id"]

    assert Booking.query.filter_by(
        centre_id=booking_data["centre_id"]
    ).count() == 1

def test_cancel_and_reactivate_booking(client, booking_data):
    """Verify cancellation releases capacity and reactivation checks availability."""

    # Create the original booking.
    response = client.post(
        "/api/bookings/",
        json=booking_data
    )

    assert response.status_code == 201
    booking_id = response.get_json()["id"]

    # Cancel the booking to release the reserved place.
    response = client.patch(
        f"/api/bookings/{booking_id}",
        json={"status": "cancelled"}
    )

    assert response.status_code == 200

    # Create another support request.
    second_request = SupportRequest(
        description="Another resident needs cooling space",
        category="cooling_space",
        resident_id=Resident.query.first().id,
        area_id=Area.query.first().id
    )

    db.session.add(second_request)
    db.session.commit()

    # Book the place released by the cancellation.
    response = client.post(
        "/api/bookings/",
        json={
            "request_id": second_request.id,
            "centre_id": booking_data["centre_id"]
        }
    )

    assert response.status_code == 201

    # Attempt to reactivate the cancelled booking.
    response = client.patch(
        f"/api/bookings/{booking_id}",
        json={"status": "approved"}
    )

    assert response.status_code == 409
    assert response.is_json

    db.session.expire_all()

    booking = db.session.get(Booking, booking_id)
    assert booking.status == "cancelled"

def test_reject_booking_with_missing_required_fields(client):
    """Verify invalid booking input returns a JSON HTTP 400 error."""
    response = client.post("/api/bookings/", json={})

    assert response.status_code == 400
    assert response.is_json
    assert response.get_json()