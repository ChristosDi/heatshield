
"""Booking routes: handle input, call services and return JSON."""

from flask.views import MethodView
from flask_smorest import Blueprint, abort

from . import service
from .schemas import (
    BookingCreateSchema,
    BookingUpdateSchema,
    BookingResponseSchema,
    BookingFilterSchema
)

blp = Blueprint(
    "bookings",
    __name__,
    url_prefix="/api/bookings",
    description="Cooling-space booking management"
)


# GET ALL / CREATE
@blp.route("/")
class BookingList(MethodView):

    @blp.arguments(BookingFilterSchema, location="query")
    @blp.response(200, BookingResponseSchema(many=True))
    def get(self, filters):
        """Retrieve and filter cooling-space bookings."""

        return service.get_all_bookings(filters)

    @blp.arguments(BookingCreateSchema)
    @blp.response(201, BookingResponseSchema)
    def post(self, data):
        """Create a pending cooling-space booking."""

        try:
            return service.create_booking(data)

        except LookupError as error:
            abort(404, message=str(error))

        except service.CentreAvailabilityError as error:
            abort(409, message=str(error))

        except ValueError as error:
            abort(400, message=str(error))


# GET ONE / UPDATE ONE / DELETE ONE
@blp.route("/<int:booking_id>")
class BookingDetail(MethodView):

    @blp.response(200, BookingResponseSchema)
    def get(self, booking_id):
        """Retrieve a specific booking."""

        booking = service.get_booking(booking_id)

        if booking is None:
            abort(404, message="Booking not found")

        return booking

    @blp.arguments(BookingUpdateSchema)
    @blp.response(200, BookingResponseSchema)
    def patch(self, data, booking_id):
        """Update a booking's status or cooling centre."""

        try:
            return service.update_booking(booking_id, data)

        except LookupError as error:
            abort(404, message=str(error))

        except service.CentreAvailabilityError as error:
            abort(409, message=str(error))

        except ValueError as error:
            abort(400, message=str(error))

    @blp.response(204)
    def delete(self, booking_id):
        """Delete a booking."""

        booking = service.get_booking(booking_id)

        if booking is None:
            abort(404, message="Booking not found")

        service.delete_booking(booking)
