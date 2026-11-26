"""Services: booking management and capacity validation."""

from sqlalchemy import text
from ..centres.models import CoolingCentre
from ..extensions import db
from ..requests.models import SupportRequest
from .constants import ACTIVE_BOOKING_STATUSES
from .models import Booking


class CentreAvailabilityError(Exception):
    """Raised when a cooling centre is closed or has no available spaces."""

def begin_booking_transaction():
    """Get an SQLite write lock before validating booking capacity -
    other transactions must wait for this one to finish"""

    db.session.execute(text("BEGIN IMMEDIATE"))


def get_all_bookings(filters=None):
    """Retrieve all bookings, optionally applying filters."""

    query = Booking.query

    if filters:
        if filters.get("request_id"):
            query = query.filter_by(
                request_id=filters["request_id"]
            )

        if filters.get("centre_id"):
            query = query.filter_by(
                centre_id=filters["centre_id"]
            )

        if filters.get("status"):
            query = query.filter_by(
                status=filters["status"]
            )

    return query.order_by(Booking.created_at.desc()).all()


def get_booking(booking_id):
    """Retrieve a booking by its ID."""

    return db.session.get(Booking, booking_id)


def check_centre_availability(centre, exclude_booking_id=None):
    """Check whether a cooling centre is open and has capacity."""

    if centre.status != "open":
        raise CentreAvailabilityError("Cooling centre is closed")

    query = Booking.query.filter(
        Booking.centre_id == centre.id,
        Booking.status.in_(ACTIVE_BOOKING_STATUSES)
    )

    # Exclude the current booking when updating or reassigning.
    if exclude_booking_id is not None:
        query = query.filter(
            Booking.id != exclude_booking_id
        )

    occupied_places = query.count()

    if occupied_places >= centre.capacity:
        raise CentreAvailabilityError("Cooling centre is at full capacity")

    return True


def create_booking(data):
    """Create a pending booking after validating the request and centre."""

    #get the write lock before checking centre availability
    begin_booking_transaction()

    support_request = db.session.get(
        SupportRequest,
        data["request_id"]
    )

    if support_request is None:
        raise LookupError("Support request not found")

    if support_request.category != "cooling_space":
        raise ValueError(
            "Only cooling-space requests can have bookings"
        )

    centre = db.session.get(
        CoolingCentre,
        data["centre_id"]
    )

    if centre is None:
        raise LookupError("Cooling centre not found")

    check_centre_availability(centre)

    booking = Booking(
        request_id=support_request.id,
        centre_id=centre.id,
        status="pending"
    )

    db.session.add(booking)
    db.session.commit()

    return booking


def update_booking(booking_id, data):
    """Update a booking after validating centre availability."""

    begin_booking_transaction()

    booking = get_booking(booking_id)

    if booking is None:
        raise LookupError("Booking not found")

    new_centre_id = data.get("centre_id", booking.centre_id)
    new_status = data.get("status", booking.status)

    centre = db.session.get(CoolingCentre, new_centre_id)

    if centre is None:
        raise LookupError("Cooling centre not found")

    # Validate availability before saving an active booking.
    if new_status in ACTIVE_BOOKING_STATUSES:
        check_centre_availability(
            centre,
            exclude_booking_id=booking.id
        )


    # Apply changes only after validation succeeds.
    booking.centre_id = new_centre_id
    booking.status = new_status

    db.session.commit()

    return booking


def delete_booking(booking):
    """Delete a booking from the database."""

    db.session.delete(booking)
    db.session.commit()
