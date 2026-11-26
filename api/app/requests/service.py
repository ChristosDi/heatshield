"""Support request rules. This is the only place they live."""

from sqlalchemy import func, or_
from werkzeug.exceptions import abort

from ..areas.models import Area
from ..extensions import db
from ..residents.models import Resident
from .constants import STATUSES

# Pull the models from their respective domains
from .models import SupportRequest


def create_request(data):
    """Create a new support request, validating foreign keys first."""

    print("CREATE REQUEST CALLED")
    print("DATA RECEIVED:", data)
    # 1. Check the Resident exists
    resident = db.session.get(Resident, data["resident_id"])
    if not resident:
        abort(400, description=f"Resident with ID {data['resident_id']} does not exist.")

    # 2. Check the Area exists (only if one was provided)
    area_id = data.get("area_id")
    if area_id is not None:
        area = db.session.get(Area, area_id)
        if not area:
            abort(400, description=f"Area with ID {area_id} does not exist.")

    # 3. Safe to create
    support_request = SupportRequest(
        # reference=data["reference"].strip(),
        description=data["description"].strip(),
        category=data["category"],
        resident_id=data["resident_id"],
        area_id=area_id,
        operational_priority=data.get("operational_priority", "normal"),
        status=data.get("status", "pending"),
    )

    db.session.add(support_request)
    db.session.commit()

    return support_request


def get_all_requests(filters=None):
    """Fetch all requests, optionally filtered by search, status, category, etc."""
    query = SupportRequest.query

    if filters:
        # 1. Direct field matches
        for field in ["category", "status", "operational_priority"]:
            value = filters.get(field)
            if value is not None:
                query = query.filter(getattr(SupportRequest, field) == value)

        # 2. Filter by Area ID
        area_id = filters.get("area_id")
        if area_id is not None:
            query = query.filter(SupportRequest.area_id == area_id)

        # 3. Search term (matches Reference, Description, or Resident Name)
        search = filters.get("search")
        if search:
            search_term = f"%{search.strip()}%"
            # Join Resident to search by their name, and use 'or_' for multiple columns
            query = query.outerjoin(Resident).filter(
                or_(
                    SupportRequest.reference.ilike(search_term),
                    SupportRequest.description.ilike(search_term),
                    Resident.display_name.ilike(search_term),
                )
            )

    return query.order_by(SupportRequest.created_at.desc()).all()


def get_request_by_id(request_id):
    """Fetch a single support request by its primary key."""
    return db.session.get(SupportRequest, request_id)

def get_request_by_reference(reference):
    """Fetch a single support request by its reference value."""
    return SupportRequest.query.filter_by(reference=reference).first()


def update_request(support_request, data):
    """Update an existing support request."""

    # Prevent updating immutable/relational fields through generic assignment
    allowed_fields = [
        "description",
        "category",
        "area_id",
        "operational_priority",
        "status",
    ]

    for field, value in data.items():
        if field in allowed_fields:
            setattr(support_request, field, value)

    db.session.commit()

    return support_request


def delete_request(request):
    """Delete a support request."""
    db.session.delete(request)
    db.session.commit()


def count_by_status():
    """Count the stored requests in each status, for example {"pending": 2, "completed": 3, ...}.

    The database does the counting in one query. A status with no requests counts as 0.
    """
    rows = db.session.execute(
        db.select(SupportRequest.status, func.count(SupportRequest.id)).group_by(
            SupportRequest.status
        )
    ).all()

    counts = dict.fromkeys(STATUSES, 0)
    counts.update(dict(rows))

    return counts
