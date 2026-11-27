from ..extensions import db


class HeatwaveSession(db.Model):
    __tablename__ = "heatwave_sessions"
    id = db.Column(db.Integer, primary_key=True)
    starts_at = db.Column(db.DateTime(timezone=True), nullable=False)
    ends_at = db.Column(db.DateTime(timezone=True), nullable=False)

    # Foreign keys
    volunteer_id = db.Column(db.Integer, db.ForeignKey("volunteers.id"), nullable=True)

    # Relationships
    volunteer = db.relationship("Volunteer", back_populates="heatwave_sessions")
    # 'covers' relationship is handled in Booking model
