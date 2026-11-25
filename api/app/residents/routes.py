
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from marshmallow import Schema, fields, validate

from ..extensions import db
from .models import Resident

blp = Blueprint(
    "residents",
    __name__,
    url_prefix="/api/residents",
    description="Operations for managing residents",
)


class ResidentOptionSchema(Schema):
    id = fields.Integer(dump_only=True)
    display_name = fields.String(
        required=True,
        validate=validate.Length(min=1, max=100),
    )
    contact_phone = fields.String(
        allow_none=True,
        validate=validate.Length(max=20),
    )
    postcode = fields.String(
        allow_none=True,
        validate=validate.Length(max=10),
    )


@blp.route("/")
class ResidentList(MethodView):

    @blp.response(200, ResidentOptionSchema(many=True))
    def get(self):
        """Return residents for dropdowns."""
        return Resident.query.order_by(Resident.display_name).all()

    @blp.arguments(ResidentOptionSchema)
    @blp.response(201, ResidentOptionSchema)
    def post(self, data):
        """Create a new resident."""
        resident = Resident(
            display_name=data["display_name"].strip(),
            contact_phone=data.get("contact_phone"),
            postcode=data.get("postcode"),
        )

        if not resident.display_name:
            abort(400, message="Resident name cannot be empty.")

        db.session.add(resident)
        db.session.commit()

        return resident
