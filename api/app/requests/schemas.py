"""Schemas: validate support request input and shape the JSON output."""
from marshmallow import Schema, fields, validate
from .constants import PRIORITIES, STATUSES, CATEGORIES


class RequestCreateSchema(Schema):

    description = fields.String(
        required=True,
        validate=validate.Length(min=1, max=2000)
    )

    category = fields.String(
        required=True,
        validate=validate.OneOf(CATEGORIES)
    )

    area = fields.String(
        allow_none=False,
        load_default=None
    )
    
    status = fields.String(
        validate=validate.OneOf(STATUSES),
        load_default="pending"
    )
    
    priority = fields.String(
        validate=validate.OneOf(PRIORITIES),
        load_default="normal"
    )


class RequestUpdateSchema(Schema):

    description = fields.String(
        validate=validate.Length(min=1, max=2000)
    )
    
    area = fields.String(allow_none=False)

    status = fields.String(
        validate=validate.OneOf(STATUSES)
    )

    priority = fields.String(
        validate=validate.OneOf(PRIORITIES)
    )


class RequestResponseSchema(Schema):

    id = fields.Integer(dump_only=True)
    description = fields.String()
    category = fields.String()
    priority = fields.String()
    status = fields.String()
    area = fields.String(allow_none=False)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    

class RequestFilterSchema(Schema):

    category = fields.String()
    status = fields.String()
    priority = fields.String()
    area = fields.Integer()