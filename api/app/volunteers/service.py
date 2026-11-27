from ..extensions import db
from .models import Volunteer


def get_all_volunteers():
    return Volunteer.query.order_by(Volunteer.display_name.asc()).all()

def create_volunteer(display_name):
    vol = Volunteer(display_name=display_name)
    db.session.add(vol)
    db.session.commit()
    return vol