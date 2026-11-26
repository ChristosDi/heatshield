from flask.views import MethodView
from flask_smorest import Blueprint, abort

from . import service
from .schemas import AreaCreateSchema, AreaOptionSchema, AreaResponseSchema


blp = Blueprint(
    "areas",
    __name__,
    url_prefix="/api/areas",
    description="Operations for managing areas",
)


@blp.route("/")
class AreaList(MethodView):

    @blp.response(200, AreaOptionSchema(many=True))
    def get(self):
        """Return areas for dropdowns."""
        return service.get_all_areas()

    @blp.arguments(AreaCreateSchema)
    @blp.response(201, AreaResponseSchema)
    def post(self, data):
        """Create an area."""
        try:
            return service.create_area(data)
        except ValueError as error:
            abort(400, message=str(error))