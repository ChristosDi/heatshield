"""Schemas: shape the report numbers as JSON."""
from marshmallow import Schema, fields


class RequestCountsSchema(Schema):
    """How many support requests are outstanding, completed and rejected."""

    outstanding = fields.Integer(
        required=True,
        metadata={"description": "Requests still being worked on: pending or in progress.", "example": 3}
    )

    completed = fields.Integer(
        required=True,
        metadata={"description": "Requests that are completed.", "example": 3}
    )

    rejected = fields.Integer(
        required=True,
        metadata={"description": "Requests that were rejected, so neither outstanding nor completed.", "example": 1}
    )

    total = fields.Integer(
        required=True,
        metadata={"description": "All stored requests. Equals outstanding + completed + rejected.", "example": 7}
    )