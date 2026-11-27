from ..extensions import db


class WelfareVisit(db.Model):
    """Dashed box in ERD - Future/Concept Idea"""
    __tablename__ = "welfare_visits"

    id = db.Column(db.Integer, primary_key=True)
    scheduled_for = db.Column(db.DateTime(timezone=True), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="scheduled")
    
    # Relationships
    volunteer_id = db.Column(db.Integer, db.ForeignKey("volunteers.id"), nullable=False)
    request_id = db.Column(db.Integer, db.ForeignKey("support_requests.id"), nullable=False)

    volunteer = db.relationship("Volunteer", back_populates="welfare_visits")
    request = db.relationship("SupportRequest", back_populates="welfare_visits")