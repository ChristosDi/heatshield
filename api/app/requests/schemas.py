
"""Schemas: validate support request input and shape the JSON output."""

from marshmallow import Schema, fields, validate
from .constants import PRIORITIES, STATUSES, CATEGORIES


class RequestCreateSchema(Schema):
    """Schema for creating a new support request."""

    description = fields.String(
        required=True,
        validate=validate.Length(min=1, max=2000),
        metadata={
            "description": "Detailed description of the support request. Must contain between 1 and 2000 characters.",
            "example": "The cooling system in the main welfare area is not functioning."
        }
    )

    category = fields.String(
        required=True,
        validate=validate.OneOf(CATEGORIES),
        metadata={
            "description": "Category of support required. Must be one of the predefined support request categories.",
            "enum": CATEGORIES,
            "example": "cooling_space"
        }
    )

    area = fields.String(
        allow_none=False,
        load_default=None,
        metadata={
            "description": "Name or identifier of the area associated with the support request. Optional when creating a request.",
            "example": "Manchester Central"
        }
    )

    status = fields.String(
        validate=validate.OneOf(STATUSES),
        load_default="pending",
        metadata={
            "description": "Current status of the support request. Defaults to pending when not provided.",
            "enum": STATUSES,
            "example": "pending"
        }
    )

    priority = fields.String(
        validate=validate.OneOf(PRIORITIES),
        load_default="normal",
        metadata={
            "description": "Urgency level assigned to the support request. Defaults to normal when not provided.",
            "enum": PRIORITIES,
            "example": "normal"
        }
    )


class RequestUpdateSchema(Schema):
    """Schema for updating an existing support request."""

    description = fields.String(
        validate=validate.Length(min=1, max=2000),
        metadata={
            "description": "Updated description of the support request. Must contain between 1 and 2000 characters.",
            "example": "The cooling system has stopped working completely."
        }
    )

    area = fields.String(
        allow_none=False,
        metadata={
            "description": "Updated name or identifier of the area associated with the request.",
            "example": "Manchester North"
        }
    )

    status = fields.String(
        validate=validate.OneOf(STATUSES),
        metadata={
            "description": "Updated status of the support request.",
            "enum": STATUSES,
            "example": "in_progress"
        }
    )

    priority = fields.String(
        validate=validate.OneOf(PRIORITIES),
        metadata={
            "description": "Updated urgency level of the support request.",
            "enum": PRIORITIES,
            "example": "high"
        }
    )


class RequestResponseSchema(Schema):
    """Schema for support request API responses."""

    id = fields.Integer(
        dump_only=True,
        metadata={
            "description": "Unique identifier of the support request.",
            "example": 101
        }
    )

    description = fields.String(
        metadata={
            "description": "Detailed description of the support request.",
            "example": "The cooling system in the main welfare area is not functioning."
        }
    )

    category = fields.String(
        validate=validate.OneOf(CATEGORIES),
        metadata={
            "description": "Category of support required.",
            "enum": CATEGORIES,
            "example": "cooling_space"
        }
    )

    priority = fields.String(
        validate=validate.OneOf(PRIORITIES),
        metadata={
            "description": "Urgency level assigned to the support request.",
            "enum": PRIORITIES,
            "example": "high"
        }
    )

    status = fields.String(
        validate=validate.OneOf(STATUSES),
        metadata={
            "description": "Current status of the support request.",
            "enum": STATUSES,
            "example": "in_progress"
        }
    )

    area = fields.String(
        allow_none=False,
        metadata={
            "description": "Name or identifier of the area associated with the support request.",
            "example": "Manchester Central"
        }
    )

    created_at = fields.DateTime(
        metadata={
            "description": "Date and time when the support request was created.",
            "example": "2026-11-23T09:30:00"
        }
    )

    updated_at = fields.DateTime(
        metadata={
            "description": "Date and time when the support request was last updated.",
            "example": "2026-11-23T10:15:00"
        }
    )


class RequestFilterSchema(Schema):
    """Schema for filtering support requests."""

    category = fields.String(
        validate=validate.OneOf(CATEGORIES),
        metadata={
            "description": "Filter support requests by category.",
            "enum": CATEGORIES,
            "example": "cooling_space"
        }
    )

    status = fields.String(
        validate=validate.OneOf(STATUSES),
        metadata={
            "description": "Filter support requests by their current status.",
            "enum": STATUSES,
            "example": "pending"
        }
    )

    priority = fields.String(
        validate=validate.OneOf(PRIORITIES),
        metadata={
            "description": "Filter support requests by urgency level.",
            "enum": PRIORITIES,
            "example": "urgent"
        }
    )

    area = fields.String(
        metadata={
            "description": "Filter support requests by area name or identifier.",
            "example": "Manchester Central"
        }
    )
