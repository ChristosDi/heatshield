from ..extensions import db


class Resident(db.Model):
    __tablename__ = "residents"

    id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String(100), nullable=False)
    contact_phone = db.Column(db.String(20), nullable=True)
    postcode = db.Column(db.String(10), nullable=True)

    # Relationships
    requests = db.relationship("SupportRequest", back_populates="resident")
