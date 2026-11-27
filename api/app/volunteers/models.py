from ..extensions import db


class Volunteer(db.Model):
    __tablename__ = "volunteers"

    id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String(100), nullable=False)

    # Relationships based on ERD
    welfare_visits = db.relationship("WelfareVisit", back_populates="volunteer")
    heatwave_sessions = db.relationship("HeatwaveSession", back_populates="volunteer")