from flask.views import MethodView
from flask_smorest import Blueprint

from . import service
from .schemas import VolunteerResponseSchema

blp = Blueprint("volunteers", __name__, url_prefix="/api/volunteers", description="Volunteers")

@blp.route("/")
class VolunteerList(MethodView):
    @blp.response(200, VolunteerResponseSchema(many=True))
    def get(self):
        return service.get_all_volunteers()