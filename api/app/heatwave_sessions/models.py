from ..extensions import db


class HeatwaveSession(db.Model):
    """Dashed box in ERD - Future/Concept Idea"""
    __tablename__ = "heatwave_sessions"

    id = db.Column(db.Integer, primary_key=True)
    starts_at = db.Column(db.DateTime(timezone=True), nullable=False)
    ends_at = db.Column(db.DateTime(timezone=True), nullable=False)
    
    # 'covers' relationship is handled in Booking model