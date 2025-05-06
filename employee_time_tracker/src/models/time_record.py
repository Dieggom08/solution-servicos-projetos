
from src.main import db # Import db from main app in src
from datetime import datetime

# Import related models for relationships
from .employee import Employee

class TimeRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employee.id"), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    record_type = db.Column(db.String(20), nullable=False) # e.g., "arrival", "lunch_start", "lunch_end", "departure"
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    photo_url = db.Column(db.String(255), nullable=True) # URL to the stored photo

    # Relationship (backref defined in Employee model)
    # employee = db.relationship("Employee", backref="time_records", lazy=True)

    def __repr__(self):
        return f"<TimeRecord {self.id} for {self.employee_id} at {self.timestamp}>"

