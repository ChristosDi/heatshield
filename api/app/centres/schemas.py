"""Schemas: validate centre and booking input and shape the JSON output."""
from marshmallow import Schema, fields, validate

CENTRE_STATUSES = ["open", "closed"]


class CoolingCentreCreateSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=150))
    capacity = fields.Integer(required=True, validate=validate.Range(min=1))
    status = fields.String(
        load_default="open",
        validate=validate.OneOf(CENTRE_STATUSES),
    )
    location = fields.String(required=True, validate=validate.Length(min=1, max=200))
    area_id = fields.Integer(required=True, validate=validate.Range(min=1))


class CoolingCentreUpdateSchema(Schema):
    name = fields.String(validate=validate.Length(min=1, max=150))
    capacity = fields.Integer(validate=validate.Range(min=1))
    status = fields.String(validate=validate.OneOf(CENTRE_STATUSES))
    location = fields.String(validate=validate.Length(min=1, max=200))
    area_id = fields.Integer(validate=validate.Range(min=1))


class CoolingCentreResponseSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String()
    capacity = fields.Integer()
    status = fields.String()
    location = fields.String()
    area_id = fields.Integer()
    free_places = fields.Integer(dump_only=True)


class CoolingCentreFilterSchema(Schema):
    area_id = fields.Integer()
    status = fields.String(validate=validate.OneOf(CENTRE_STATUSES))