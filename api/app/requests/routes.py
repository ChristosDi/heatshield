"""Support request routes: read the input, call the service, return JSON. No business rules here."""
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from . import service
from .schemas import (
    RequestCreateSchema,
    RequestFilterSchema,
    RequestResponseSchema,
    RequestUpdateSchema,
)

blp = Blueprint(
    "requests",
    __name__,
    url_prefix="/api/requests",
    description="Operations for managing support requests"
)


# GET ALL / CREATE
@blp.route("/")
class RequestList(MethodView):

    @blp.doc(summary="List support requests", description="Retrieve a list of support requests, optionally filtered by category, status, priority, area, or search term.")
    @blp.arguments(RequestFilterSchema, location="query")
    @blp.response(200, RequestResponseSchema(many=True))
    def get(self, filters):
        """Retrieve and filter support requests."""
        return service.get_all_requests(filters)

    @blp.doc(summary="Create a support request", description="Create a new support request. Requires a reference, description, category, and a valid resident ID.")
    @blp.arguments(RequestCreateSchema)
    @blp.response(201, RequestResponseSchema)
    @blp.alt_response(400, description="Invalid input data")
    def post(self, data):
        """Create a support request."""
        return service.create_request(data)


# GET ONE / UPDATE ONE / DELETE ONE
@blp.route("/<int:request_id>")
class RequestDetail(MethodView):

    @blp.doc(summary="Get a single support request", description="Retrieve the full details of a specific support request by its ID.")
    @blp.response(200, RequestResponseSchema)
    @blp.alt_response(404, description="Request not found")
    def get(self, request_id):
        """Retrieve a specific support request."""
        support_request = service.get_request(request_id)

        if support_request is None:
            abort(404, message="Request not found")

        return support_request

    @blp.doc(summary="Update a support request", description="Partially update an existing support request. Only provided fields will be changed.")
    @blp.arguments(RequestUpdateSchema(partial=True))
    @blp.response(200, RequestResponseSchema)
    @blp.alt_response(404, description="Request not found")
    def patch(self, data, request_id):
        """Update a support request."""
        support_request = service.get_request(request_id)

        if support_request is None:
            abort(404, message="Request not found")

        return service.update_request(
            support_request,
            data
        )
    
    @blp.doc(summary="Delete a support request", description="Permanently delete a support request by its ID.")
    @blp.response(204)
    @blp.alt_response(404, description="Request not found")
    def delete(self, request_id):
        """Delete a request"""
        request = service.get_request(request_id)
        
        if request is None:
            abort(404, message="Request not found")
            
        service.delete_request(request)