"""Models: Support request and Resident (ERD page 3)."""

import uuid
from datetime import UTC, datetime

from ..extensions import db


def utc_now():
    return datetime.now(UTC)


def generate_reference():
    return f"HS-{uuid.uuid4().hex[:12].upper()}"


class SupportRequest(db.Model):
    __tablename__ = "support_requests"

    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(
        db.String(50), nullable=False, unique=True, default=generate_reference
    )  # From ERD
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")
    category = db.Column(db.String(50), nullable=False)
    operational_priority = db.Column(
        db.String(20), nullable=False, default="normal"
    )  # Renamed from 'priority' to match ERD
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now, nullable=False)

    # Foreign Keys
    resident_id = db.Column(db.Integer, db.ForeignKey("residents.id"), nullable=False)
    area_id = db.Column(db.Integer, db.ForeignKey("areas.id"), nullable=True)

    # Note: 'waiting_time' is a calculated oval in the ERD (indicated by dashed lines),
    # so it should NOT be a database column. It should be a @property instead.
    @property
    def waiting_time(self):
        if self.status == "resolved":
            return None

        # SQLite strips timezones, so we must ensure both are aware
        # before doing the subtraction.
        created_at = self.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=UTC)

        return datetime.now(UTC) - created_at
