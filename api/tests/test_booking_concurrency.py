"""Verify capacity protection during concurrent booking requests."""

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from app import create_app
from app.extensions import db
from app.areas.models import Area
from app.centres.models import CoolingCentre
from app.residents.models import Resident
from app.requests.models import SupportRequest
from app.bookings.models import Booking


def test_concurrent_booking_last_available_place(tmp_path):
    """Only one concurrent request can reserve the last place."""

    database_path = tmp_path / "concurrency.db"

    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": (
            f"sqlite:///{database_path.as_posix()}"
        ),
    })

    # Arrange: create a centre with one available place.
    with app.app_context():
        db.create_all()

        area = Area(name="Bolton")
        resident = Resident(display_name="Test Resident")

        db.session.add_all([area, resident])
        db.session.flush()

        centre = CoolingCentre(
            name="Concurrency Test Centre",
            location="Bolton",
            capacity=1,
            status="open",
            area_id=area.id,
        )

        requests = [
            SupportRequest(
                description=f"Cooling request {number}",
                category="cooling_space",
                resident_id=resident.id,
                area_id=area.id,
            )
            for number in range(2)
        ]

        db.session.add_all([centre, *requests])
        db.session.commit()

        centre_id = centre.id
        request_ids = [request.id for request in requests]

    # Synchronise both booking attempts.
    barrier = Barrier(2)

    def make_booking(request_id):
        with app.test_client() as client:
            barrier.wait(timeout=10)

            response = client.post(
                "/api/bookings/",
                json={
                    "request_id": request_id,
                    "centre_id": centre_id,
                },
            )

            return response.status_code

    # Act: submit both requests concurrently.
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(
            executor.map(make_booking, request_ids)
        )

    # Assert: only one booking succeeds.
    assert sorted(results) == [201, 409]

    with app.app_context():
        assert Booking.query.filter_by(
            centre_id=centre_id
        ).count() == 1

        db.session.remove()
        db.engine.dispose()