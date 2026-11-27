from marshmallow import Schema, fields, validate

# Importing the exact constants from your requests module
from ..requests.constants import STATUSES


class WelfareVisitCreateSchema(Schema):
    """Schema for scheduling a new welfare visit."""
    scheduled_for = fields.DateTime(required=True)
    volunteer_id = fields.Integer(required=True)
    request_id = fields.Integer(required=True)
    status = fields.String(
        load_default="pending", # Defaulting to 'pending' to match your STATUSES list
        validate=validate.OneOf(STATUSES)
    )

class WelfareVisitUpdateSchema(Schema):
    """Schema for updating an existing welfare visit."""
    class Meta:
        partial = True

    scheduled_for = fields.DateTime()
    volunteer_id = fields.Integer()
    request_id = fields.Integer()
    status = fields.String(validate=validate.OneOf(STATUSES))

class WelfareVisitResponseSchema(Schema):
    """Schema for returning welfare visit data."""
    id = fields.Integer(dump_only=True)
    scheduled_for = fields.DateTime()
    status = fields.String()
    
    # Flattened relationship fields for the frontend
    volunteer_id = fields.Integer()
    volunteer_name = fields.Method("get_volunteer_name")
    
    request_id = fields.Integer()
    request_reference = fields.Method("get_request_reference")
    request_category = fields.Method("get_request_category")

    def get_volunteer_name(self, obj):
        return obj.volunteer.display_name if obj.volunteer else None

    def get_request_reference(self, obj):
        return obj.request.reference if obj.request else None

    def get_request_category(self, obj):
        return obj.request.category if obj.request else None