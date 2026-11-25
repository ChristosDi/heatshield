"""Schemas: validate support request input and shape the JSON output."""

from marshmallow import Schema, fields, validate

from .constants import CATEGORIES, PRIORITIES, STATUSES


class RequestCreateSchema(Schema):
    """Schema for creating a new support request."""

    # reference = fields.String(
    #     required=True,
    #     validate=validate.Length(min=1, max=50),
    #     metadata={
    #         "description": "Unique human-readable reference code for the request.",
    #         "example": "REQ-2026-001"
    #     }
    # )

    description = fields.String(
        required=True,
        validate=validate.Length(min=1, max=2000),
        metadata={
            "description": "Detailed description of the support request. Must contain between 1 and 2000 characters.",
            "example": "The cooling system in the main welfare area is not functioning.",
        },
    )

    category = fields.String(
        required=True,
        validate=validate.OneOf(CATEGORIES),
        metadata={
            "description": "Category of support required. Must be one of the predefined support request categories.",
            "enum": CATEGORIES,
            "example": "cooling_space",
        },
    )

    resident_id = fields.Integer(
        required=True,
        metadata={
            "description": "The ID of the resident raising the support request.",
            "example": 42,
        },
    )

    area_id = fields.Integer(
        allow_none=True,
        load_default=None,
        metadata={
            "description": "The ID of the area associated with the support request. Optional.",
            "example": 3,
        },
    )

    status = fields.String(
        validate=validate.OneOf(STATUSES),
        load_default="pending",
        metadata={
            "description": "Current status of the support request. Defaults to pending when not provided.",
            "enum": STATUSES,
            "example": "pending",
        },
    )

    operational_priority = fields.String(
        validate=validate.OneOf(PRIORITIES),
        load_default="normal",
        metadata={
            "description": "Urgency level assigned to the support request. Defaults to normal when not provided.",
            "enum": PRIORITIES,
            "example": "normal",
        },
    )

    created_at = fields.DateTime(
        metadata={
            "description": "Date and time when the support request was created.",
            "example": "2026-11-23T09:30:00",
        }
    )
    updated_at = fields.DateTime(
        metadata={
            "description": "Date and time when the support request was last.",
            "example": "2026-11-23T09:30:00",
        }
    )


class RequestUpdateSchema(Schema):
    """Schema for updating an existing support request."""

    category = fields.String(
        validate=validate.OneOf(CATEGORIES),
        metadata={
            "description": "Updated category of the support request.",
            "enum": CATEGORIES,
            "example": "cooling_space",
        },
    )

    description = fields.String(
        validate=validate.Length(min=1, max=2000),
        metadata={
            "description": "Updated description of the support request. Must contain between 1 and 2000 characters.",
            "example": "The cooling system has stopped working completely.",
        },
    )

    area_id = fields.Integer(
        allow_none=True,
        metadata={
            "description": "Updated ID of the area associated with the request. Set to null to remove the area.",
            "example": 4,
        },
    )

    status = fields.String(
        validate=validate.OneOf(STATUSES),
        metadata={
            "description": "Updated status of the support request.",
            "enum": STATUSES,
            "example": "in_progress",
        },
    )

    operational_priority = fields.String(
        validate=validate.OneOf(PRIORITIES),
        metadata={
            "description": "Updated urgency level of the support request.",
            "enum": PRIORITIES,
            "example": "high",
        },
    )


class RequestResponseSchema(Schema):
    """Schema for support request API responses."""

    id = fields.Integer(
        dump_only=True,
        metadata={
            "description": "Unique identifier of the support request.",
            "example": 101,
        },
    )

    # reference = fields.String(
    #     metadata={
    #         "description": "Unique human-readable reference code.",
    #         "example": "REQ-2026-001"
    #     }
    # )

    description = fields.String(
        metadata={
            "description": "Detailed description of the support request.",
            "example": "The cooling system in the main welfare area is not functioning.",
        }
    )

    category = fields.String(
        metadata={
            "description": "Category of support required.",
            "enum": CATEGORIES,
            "example": "cooling_space",
        },
    )

    operational_priority = fields.String(
        metadata={
            "description": "Urgency level assigned to the support request.",
            "enum": PRIORITIES,
            "example": "high",
        },
    )

    status = fields.String(
        metadata={
            "description": "Current status of the support request.",
            "enum": STATUSES,
            "example": "in_progress",
        },
    )

    # Flattened relationship fields for easier consumption by the Django frontend
    resident_id = fields.Integer(
        metadata={
            "description": "ID of the resident who raised the request.",
            "example": 42,
        }
    )

    resident_name = fields.Method("get_resident_name")

    area_id = fields.Integer(
        allow_none=True,
        metadata={"description": "ID of the associated area.", "example": 3},
    )

    area_name = fields.Method("get_area_name")

    waiting_time = fields.String(
        dump_only=True,
        metadata={
            "description": "Calculated time elapsed since creation (if not resolved).",
            "example": "2 days, 4 hours",
        },
    )

    created_at = fields.DateTime(
        metadata={
            "description": "Date and time when the support request was created.",
            "example": "2026-11-23T09:30:00",
        }
    )

    updated_at = fields.DateTime(
        metadata={
            "description": "Date and time when the support request was last updated.",
            "example": "2026-11-23T10:15:00",
        }
    )

    def get_resident_name(self, obj):
        return obj.resident.display_name if obj.resident else None

    def get_area_name(self, obj):
        return obj.area.name if obj.area else None


class RequestFilterSchema(Schema):
    """Schema for filtering support requests."""

    category = fields.String(
        validate=validate.OneOf(CATEGORIES),
        metadata={
            "description": "Filter support requests by category.",
            "enum": CATEGORIES,
            "example": "cooling_space",
        },
    )

    status = fields.String(
        validate=validate.OneOf(STATUSES),
        metadata={
            "description": "Filter support requests by their current status.",
            "enum": STATUSES,
            "example": "pending",
        },
    )

    operational_priority = fields.String(
        validate=validate.OneOf(PRIORITIES),
        metadata={
            "description": "Filter support requests by urgency level.",
            "enum": PRIORITIES,
            "example": "urgent",
        },
    )

    area_id = fields.Integer(
        metadata={"description": "Filter support requests by area ID.", "example": 3}
    )

    search = fields.String(
        metadata={
            "description": "Search term to match against description, or resident name.",
            "example": "REQ-2026",
        }
    )
