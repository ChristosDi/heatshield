"""Centre and booking routes: read the input, call the service, return JSON. No business rules here."""
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from ..extensions import db
from .models import CoolingCentre
from .schemas import (
    CoolingCentreCreateSchema,
    CoolingCentreFilterSchema,
    CoolingCentreResponseSchema,
    CoolingCentreUpdateSchema,
)

blp = Blueprint(
    "cooling_centres",
    __name__,
    url_prefix="/api/centres",
    description="Cooling centre operations",
)


@blp.route("/")
class CoolingCentreList(MethodView):

    @blp.arguments(CoolingCentreFilterSchema, location="query")
    @blp.response(200, CoolingCentreResponseSchema(many=True))
    def get(self, filters):
        query = CoolingCentre.query

        if filters.get("area_id") is not None:
            query = query.filter_by(area_id=filters["area_id"])

        if filters.get("status"):
            query = query.filter_by(status=filters["status"])

        return query.order_by(CoolingCentre.name.asc()).all()

    @blp.arguments(CoolingCentreCreateSchema)
    @blp.response(201, CoolingCentreResponseSchema)
    def post(self, data):
        centre = CoolingCentre(**data)
        db.session.add(centre)
        db.session.commit()
        return centre


@blp.route("/<int:centre_id>")
class CoolingCentreDetail(MethodView):

    @blp.response(200, CoolingCentreResponseSchema)
    def get(self, centre_id):
        centre = db.session.get(CoolingCentre, centre_id)

        if centre is None:
            abort(404, message="Cooling centre not found")

        return centre

    @blp.arguments(CoolingCentreUpdateSchema)
    @blp.response(200, CoolingCentreResponseSchema)
    def patch(self, data, centre_id):
        centre = db.session.get(CoolingCentre, centre_id)

        if centre is None:
            abort(404, message="Cooling centre not found")

        for field, value in data.items():
            setattr(centre, field, value)

        db.session.commit()
        return centre