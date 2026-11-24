"""Report routes: read the input, call the service, return JSON. No business rules here."""
from flask.views import MethodView
from flask_smorest import Blueprint

from . import service
from .schemas import RequestCountsSchema

blp = Blueprint(
    "reports",
    __name__,
    url_prefix="/api/reports",
    description="Dashboard numbers, calculated when they are asked for"
)


@blp.route("/request-counts")
class RequestCounts(MethodView):

    @blp.response(200, RequestCountsSchema)
    def get(self):
        """Count support requests: outstanding, completed, rejected and total."""

        return service.request_counts()