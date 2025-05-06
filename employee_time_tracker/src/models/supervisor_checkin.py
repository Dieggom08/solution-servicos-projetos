
from src.main import db # Import db from main app in src
from datetime import datetime

# Import related models for relationships
from .employee import Employee

class SupervisorCheckin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    supervisor_id = db.Column(db.Integer, db.ForeignKey("employee.id"), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    latitude = db.Column(db.Float, nullable=True) # Optional, depending on requirements
    longitude = db.Column(db.Float, nullable=True) # Optional, depending on requirements
    photo_url = db.Column(db.String(255), nullable=False) # URL to the stored photo
    location_name = db.Column(db.String(255), nullable=True) # e.g., Condominium Name

    # Relationship (backref defined in SupervisorQuestionnaireResponse model)
    # supervisor = db.relationship("Employee", backref="supervisor_checkins", lazy=True)

    def __repr__(self):
        return f"<SupervisorCheckin {self.id} by {self.supervisor_id} at {self.timestamp}>"

