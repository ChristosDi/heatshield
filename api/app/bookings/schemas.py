
"""Schemas: validate booking input and shape JSON output."""

from marshmallow import Schema, fields, validate


BOOKING_STATUSES = [
    "pending",
    "approved",
    "cancelled",
    "flagged"
]


class BookingCreateSchema(Schema):

    request_id = fields.Integer(
        required=True
    )

    centre_id = fields.Integer(
        required=True
    )


class BookingUpdateSchema(Schema):

    status = fields.String(
        validate=validate.OneOf(BOOKING_STATUSES)
    )

    centre_id = fields.Integer(
        validate=validate.Range(min=1)
    )


class BookingResponseSchema(Schema):

    id = fields.Integer(dump_only=True)

    request_id = fields.Integer()

    centre_id = fields.Integer()

    status = fields.String()

    created_at = fields.DateTime()

    updated_at = fields.DateTime()


class BookingFilterSchema(Schema):

    request_id = fields.Integer()

    centre_id = fields.Integer()

    status = fields.String(
        validate=validate.OneOf(BOOKING_STATUSES)
    )
