from flask.views import MethodView
from flask_smorest import Blueprint
from marshmallow import Schema, fields

from .models import Area

blp = Blueprint(
    "areas",
    __name__,
    url_prefix="/api/areas",
    description="Operations for managing areas"
)


class AreaOptionSchema(Schema):
    id = fields.Integer()
    name = fields.String()


@blp.route("/")
class AreaList(MethodView):

    @blp.response(200, AreaOptionSchema(many=True))
    def get(self):
        """Return areas for dropdowns."""
        areas = Area.query.order_by(Area.name).all()

        return [
            {
                "id": area.id,
                "name": area.name
            }
            for area in areas
        ]