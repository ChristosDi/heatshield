
"""Services: booking management and capacity validation."""

from ..extensions import db
from .models import Booking
from ..requests.models import SupportRequest
from ..centres.models import CoolingCentre
from .constants import ACTIVE_BOOKING_STATUSES


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

    if not centre.is_open:
        raise ValueError("Cooling centre is closed")

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
        raise ValueError("Cooling centre is at full capacity")

    return True


def create_booking(data):
    """Create a pending booking after validating the request and centre."""

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


def update_booking(booking, data):
    """Update a booking and validate any centre reassignment."""

    new_centre_id = data.get("centre_id")
    new_status = data.get("status")

    if new_centre_id is not None:
        centre = db.session.get(
            CoolingCentre,
            new_centre_id
        )

        if centre is None:
            raise LookupError("Cooling centre not found")

        # Check availability when changing centres.
        if centre.id != booking.centre_id:
            check_centre_availability(
                centre,
                exclude_booking_id=booking.id
            )

            booking.centre_id = centre.id

    if new_status is not None:
        # Recheck capacity before approving a booking.
        if new_status == "approved":
            centre = db.session.get(
                CoolingCentre,
                booking.centre_id
            )

            check_centre_availability(
                centre,
                exclude_booking_id=booking.id
            )

        booking.status = new_status

    db.session.commit()

    return booking


def delete_booking(booking):
    """Delete a booking from the database."""

    db.session.delete(booking)
    db.session.commit()
