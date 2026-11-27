from flask.views import MethodView
from flask_smorest import Blueprint, abort

from . import service
from .schemas import (
    WelfareVisitCreateSchema,
    WelfareVisitResponseSchema,
    WelfareVisitUpdateSchema,
)

blp = Blueprint(
    "welfare_visits",
    __name__,
    url_prefix="/api/welfare-visits",
    description="Operations for scheduling and managing welfare visits"
)

@blp.route("/")
class WelfareVisitList(MethodView):
    
    @blp.doc(summary="List welfare visits")
    @blp.response(200, WelfareVisitResponseSchema(many=True))
    def get(self):
        """Retrieve a list of all scheduled welfare visits."""
        return service.get_all_visits()

    @blp.doc(summary="Schedule a welfare visit")
    @blp.arguments(WelfareVisitCreateSchema)
    @blp.response(201, WelfareVisitResponseSchema)
    @blp.alt_response(400, description="Invalid input or missing foreign keys")
    def post(self, data):
        """Schedule a new welfare visit."""
        return service.create_visit(data)


@blp.route("/<int:visit_id>")
class WelfareVisitDetail(MethodView):

    @blp.doc(summary="Get a single welfare visit")
    @blp.response(200, WelfareVisitResponseSchema)
    @blp.alt_response(404, description="Visit not found")
    def get(self, visit_id):
        """Retrieve details of a specific welfare visit."""
        visit = service.get_visit(visit_id)
        if not visit:
            abort(404, description="Welfare visit not found")
        return visit

    @blp.doc(summary="Update a welfare visit")
    @blp.arguments(WelfareVisitUpdateSchema)
    @blp.response(200, WelfareVisitResponseSchema)
    @blp.alt_response(404, description="Visit not found")
    def patch(self, data, visit_id):
        """Update an existing welfare visit (e.g., change status to 'completed')."""
        visit = service.get_visit(visit_id)
        if not visit:
            abort(404, description="Welfare visit not found")
        return service.update_visit(visit, data)

    @blp.doc(summary="Delete a welfare visit")
    @blp.response(204)
    @blp.alt_response(404, description="Visit not found")
    def delete(self, visit_id):
        """Delete a welfare visit."""
        visit = service.get_visit(visit_id)
        if not visit:
            abort(404, description="Welfare visit not found")
        service.delete_visit(visit)