"""Model: Area (ERD page 3)."""
from ..extensions import db


class Area(db.Model):
    __tablename__ = "areas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    # Relationships
    requests = db.relationship("SupportRequest", backref="area", lazy=True)
    cooling_centres = db.relationship("CoolingCentre", backref="area", lazy=True)
