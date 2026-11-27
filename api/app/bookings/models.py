from datetime import UTC, datetime

from ..extensions import db


def utc_now():
    return datetime.now(UTC)


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey("support_requests.id"), nullable=False)
    centre_id = db.Column(db.Integer, db.ForeignKey("cooling_centres.id"), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    request = db.relationship("SupportRequest", backref=db.backref("bookings", lazy=True))
    centre = db.relationship("CoolingCentre", backref=db.backref("bookings", lazy=True))
    
    # Note: 'covers' is a dotted diamond connecting to Heatwave Session, meaning it's a future idea.
    # I've added a nullable FK here for future-proofing.
    session_id = db.Column(db.Integer, db.ForeignKey("heatwave_sessions.id"), nullable=True)
