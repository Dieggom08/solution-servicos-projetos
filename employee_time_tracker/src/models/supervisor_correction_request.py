
from src.main import db # Import db from main app in src
from datetime import datetime
from sqlalchemy.dialects.mysql import LONGTEXT

# Import related models for relationships
from .employee import Employee
from .time_record import TimeRecord

class SupervisorCorrectionRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    supervisor_id = db.Column(db.Integer, db.ForeignKey("employee.id"), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey("employee.id"), nullable=False) # Employee whose record needs correction
    # Optional: Link to a specific time record being corrected
    time_record_id = db.Column(db.Integer, db.ForeignKey("time_record.id"), nullable=True)
    request_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    requested_change_type = db.Column(db.String(50), nullable=False) # e.g., "arrival_time", "departure_time", "lunch_start", "lunch_end", "absence_justification"
    original_value = db.Column(db.String(255), nullable=True) # Original time or status
    requested_value = db.Column(db.String(255), nullable=False) # Requested new time or justification text
    reason = db.Column(LONGTEXT, nullable=False) # Reason for the correction

    status = db.Column(db.String(50), nullable=False, default="pending") # pending, approved, rejected
    admin_notes = db.Column(LONGTEXT, nullable=True) # Notes from admin who reviewed the request
    reviewed_at = db.Column(db.DateTime, nullable=True)
    reviewed_by_admin_id = db.Column(db.Integer, db.ForeignKey("employee.id"), nullable=True)

    # Relationships
    supervisor = db.relationship("Employee", foreign_keys=[supervisor_id], backref=db.backref("submitted_correction_requests", lazy=True))
    employee = db.relationship("Employee", foreign_keys=[employee_id], backref=db.backref("correction_requests_for", lazy=True))
    time_record = db.relationship("TimeRecord", backref=db.backref("correction_request", uselist=False, lazy=True))
    reviewed_by_admin = db.relationship("Employee", foreign_keys=[reviewed_by_admin_id], backref=db.backref("reviewed_correction_requests", lazy=True))

    def __repr__(self):
        return f"<SupervisorCorrectionRequest {self.id} for employee {self.employee_id} by supervisor {self.supervisor_id}>"

