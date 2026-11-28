"""Area rules. This is the only place they live."""
from ..extensions import db
from .models import Area


def get_all_areas():
    return Area.query.order_by(Area.name).all()


def create_area(data):
    name = data["name"].strip()

    if not name:
        raise ValueError("Area name cannot be blank")

    area = Area(name=name)
    db.session.add(area)
    db.session.commit()

    return area