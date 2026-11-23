"""Models: Support request and Resident (ERD page 3)."""
from datetime import datetime, timezone

from ..extensions import db

class SupportRequest(db.Model):

    __tablename__ = "support_requests"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    category = db.Column(
        db.String(50),
        nullable=False
    )

    priority = db.Column(
        db.String(20),
        nullable=False,
        default="normal"
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="pending"
    )

    area = db.Column(
        db.Text,
        nullable=False
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