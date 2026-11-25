"""Models: Cooling centre and Booking (ERD page 3)."""
from ..extensions import db


class CoolingCentre(db.Model):
    __tablename__ = "cooling_centres"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="open") # ERD uses 'status' instead of 'is_open'
    closed_at = db.Column(db.DateTime(timezone=True), nullable=True)
    location = db.Column(db.String(200), nullable=False)
    
    # Foreign Keys
    area_id = db.Column(db.Integer, db.ForeignKey("areas.id"), nullable=False)

    # Note: 'free_places', 'accessibility_features' are dashed ovals (calculated/not stored)
    @property
    def free_places(self):
        booked = sum(1 for b in self.bookings if b.status in ["confirmed", "pending"])
        return self.capacity - booked