"""Support request routes: read the input, call the service, return JSON. No business rules here."""
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from . import service
from .schemas import (
    RequestCreateSchema,
    RequestUpdateSchema,
    RequestResponseSchema,
    RequestFilterSchema
)

blp = Blueprint(
    "requests",
    __name__,
    url_prefix="/api/requests",
    description="Support request management"
)


# GET ALL / CREATE
@blp.route("/")
class RequestList(MethodView):

    @blp.arguments(RequestFilterSchema, location="query")
    @blp.response(200, RequestResponseSchema(many=True))
    def get(self, filters):
        """Retrieve and filter support requests."""

        return service.get_all_requests(filters)

    @blp.arguments(RequestCreateSchema)
    @blp.response(201, RequestResponseSchema)
    def post(self, data):
        """Create a support request."""

        return service.create_request(data)


# GET ONE / UPDATE ONE
@blp.route("/<int:request_id>")
class RequestDetail(MethodView):

    @blp.response(200, RequestResponseSchema)
    def get(self, request_id):
        """Retrieve a specific support request."""

        support_request = service.get_request(request_id)

        if support_request is None:
            abort(404, message="Request not found")

        return support_request

    @blp.arguments(RequestUpdateSchema)
    @blp.response(200, RequestResponseSchema)
    def patch(self, data, request_id):
        """Update a support request."""

        support_request = service.get_request(request_id)

        if support_request is None:
            abort(404, message="Request not found")

        return service.update_request(
            support_request,
            data
        )
    
    @blp.response(204)
    def delete(self, request_id):
        """Delete a request"""
        
        request = service.get_request(request_id)
        
        if request is None:
            abort(404, message="Request not found")
            
        service.delete_request(request)