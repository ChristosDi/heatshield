"""Models: Cooling centre and Booking (ERD page 3)."""

from ..extensions import db


class CoolingCentre(db.Model):

    __tablename__ = "cooling_centres"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(150),
        nullable=False
    )

    location = db.Column(
        db.String(200),
        nullable=False
    )

    capacity = db.Column(
        db.Integer,
        nullable=False
    )

    is_open = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )
