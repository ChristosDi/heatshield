"""Support request rules. This is the only place they live."""
from ..extensions import db
from .models import SupportRequest


def create_request(data):

    support_request = SupportRequest(
        description=data["description"].strip(),
        category=data["category"],
        area=data.get("area"),
        priority=data.get("priority", "normal"),
        status=data.get("status", "pending")
    )

    db.session.add(support_request)
    db.session.commit()

    return support_request


def get_all_requests(filters=None):

    query = SupportRequest.query

    if filters:

        for field in ["category", "status", "priority", "area"]:

            value = filters.get(field)

            if value is not None:
                query = query.filter(
                    getattr(SupportRequest, field) == value
                )

    return query.order_by(
        SupportRequest.created_at.desc()
    ).all()


def get_request(request_id):

    return db.session.get(
        SupportRequest,
        request_id
    )


def update_request(support_request, data):

    for field, value in data.items():
        setattr(support_request, field, value)

    db.session.commit()

    return support_request

def delete_request(request): 
    db.session.delete(request)
    db.session.commit()