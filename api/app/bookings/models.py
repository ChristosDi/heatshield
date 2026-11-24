"""Models: Cooling-space bookings."""

from datetime import datetime, timezone

from ..extensions import db


class Booking(db.Model):

    __tablename__ = "bookings"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    request_id = db.Column(
        db.Integer,
        db.ForeignKey("support_requests.id"),
        nullable=False
    )

    centre_id = db.Column(
        db.Integer,
        db.ForeignKey("cooling_centres.id"),
        nullable=False
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="pending"
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    request = db.relationship(
        "SupportRequest",
        backref=db.backref("bookings", lazy=True)
    )

    centre = db.relationship(
        "CoolingCentre",
        backref=db.backref("bookings", lazy=True)
    )
