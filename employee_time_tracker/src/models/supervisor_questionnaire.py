
from src.main import db # Import db from main app in src
from datetime import datetime
from sqlalchemy.dialects.mysql import LONGTEXT

# Import related models for relationships
from .employee import Employee
from .supervisor_checkin import SupervisorCheckin

class SupervisorQuestionnaireResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    supervisor_id = db.Column(db.Integer, db.ForeignKey("employee.id"), nullable=False)
    # Optional: Link to a specific check-in for context
    checkin_id = db.Column(db.Integer, db.ForeignKey("supervisor_checkin.id"), nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # Store client/location info if not relying solely on checkin_id
    # client_id = db.Column(db.Integer, nullable=True) # Or String for client code
    # location_name = db.Column(db.String(255), nullable=True)

    strengths_text = db.Column(LONGTEXT, nullable=True)
    strengths_photo_url = db.Column(db.String(255), nullable=True) # URL to the stored photo
    improvements_text = db.Column(LONGTEXT, nullable=True)
    employee_wellbeing_text = db.Column(LONGTEXT, nullable=True)
    observations_text = db.Column(LONGTEXT, nullable=True)

    # Relationships
    supervisor = db.relationship("Employee", foreign_keys=[supervisor_id], backref=db.backref("questionnaire_responses", lazy=True))
    checkin = db.relationship("SupervisorCheckin", backref=db.backref("questionnaire_response", uselist=False, lazy=True))

    def __repr__(self):
        return f"<SupervisorQuestionnaireResponse {self.id} by {self.supervisor_id} at {self.timestamp}>"

