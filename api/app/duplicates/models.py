from ..extensions import db


class DuplicateMatch(db.Model):
    """Dashed box in ERD - Future/Concept Idea"""
    __tablename__ = "duplicate_matches"

    id = db.Column(db.Integer, primary_key=True)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")
    
    # ERD shows 'new' and 'existing' relationships to SupportRequest
    new_request_id = db.Column(db.Integer, db.ForeignKey("support_requests.id"), nullable=False)
    existing_request_id = db.Column(db.Integer, db.ForeignKey("support_requests.id"), nullable=False)

    new_request = db.relationship("SupportRequest", foreign_keys=[new_request_id])
    existing_request = db.relationship("SupportRequest", foreign_keys=[existing_request_id])