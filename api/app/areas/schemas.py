"""Schemas: shape area data as JSON."""
from marshmallow import Schema, fields, validate


class AreaCreateSchema(Schema):
    name = fields.String(
        required=True,
        validate=validate.Length(min=1, max=100),
    )


class AreaResponseSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String()


class AreaOptionSchema(Schema):
    id = fields.Integer()
    name = fields.String()