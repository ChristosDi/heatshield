from flask_smorest import abort

from ..extensions import db
from ..requests.models import SupportRequest
from ..volunteers.models import Volunteer
from .models import WelfareVisit


def create_visit(data):
    """Schedule a new welfare visit."""
    # 1. Validate Foreign Keys
    if not db.session.get(Volunteer, data["volunteer_id"]):
        abort(400, description=f"Volunteer with ID {data['volunteer_id']} does not exist.")
        
    if not db.session.get(SupportRequest, data["request_id"]):
        abort(400, description=f"Support Request with ID {data['request_id']} does not exist.")

    # 2. Create
    visit = WelfareVisit(
        scheduled_for=data["scheduled_for"],
        volunteer_id=data["volunteer_id"],
        request_id=data["request_id"],
        status=data.get("status", "pending") # Using your exact constant default
    )

    db.session.add(visit)
    db.session.commit()
    return visit

def get_all_visits(filters=None):
    """Fetch visits, optionally filtered by status or volunteer."""
    query = WelfareVisit.query

    if filters:
        if status := filters.get("status"):
            query = query.filter(WelfareVisit.status == status)
        if volunteer_id := filters.get("volunteer_id"):
            query = query.filter(WelfareVisit.volunteer_id == volunteer_id)

    return query.order_by(WelfareVisit.scheduled_for.asc()).all()

def get_visit(visit_id):
    """Fetch a single visit by ID."""
    return db.session.get(WelfareVisit, visit_id)

def update_visit(visit, data):
    """Update an existing visit."""
    # If they are trying to reassign the visit, validate the new IDs
    if "volunteer_id" in data and not db.session.get(Volunteer, data["volunteer_id"]):
        abort(400, description=f"Volunteer with ID {data['volunteer_id']} does not exist.")
        
    if "request_id" in data and not db.session.get(SupportRequest, data["request_id"]):
        abort(400, description=f"Support Request with ID {data['request_id']} does not exist.")

    for field, value in data.items():
        setattr(visit, field, value)

    db.session.commit()
    return visit

def delete_visit(visit):
    """Delete a visit."""
    db.session.delete(visit)
    db.session.commit()