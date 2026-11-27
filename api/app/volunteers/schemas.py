from marshmallow import Schema, fields


class VolunteerResponseSchema(Schema):
    id = fields.Integer(dump_only=True)
    display_name = fields.String(required=True)