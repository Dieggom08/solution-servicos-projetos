
from src.main import db # Import db from main app in src
from datetime import datetime, timedelta

# Import related models for relationships
from .employee import Employee
from .material import MaterialType # Corrected import

class MaterialLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    material_type_id = db.Column(db.Integer, db.ForeignKey("material_type.id"), nullable=False) # Corrected ForeignKey
    employee_id = db.Column(db.Integer, db.ForeignKey("employee.id"), nullable=False) # Employee receiving the material
    delivery_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    # Optional: Photo confirming delivery or usage (e.g., cleaning photo)
    photo_url = db.Column(db.String(255), nullable=True)
    # Optional: Notes about the delivery or condition
    notes = db.Column(db.Text, nullable=True)
    # Optional: Link to a specific supervisor check-in if delivery happened during one
    checkin_id = db.Column(db.Integer, db.ForeignKey("supervisor_checkin.id"), nullable=True)
    # Calculated field for expected replacement date
    expected_replacement_date = db.Column(db.Date, nullable=True)

    # Relationships
    material_type = db.relationship("MaterialType", backref=db.backref("logs", lazy=True))
    # Removed backref from employee relationship to resolve conflict
    employee = db.relationship("Employee") # Removed backref="material_logs"
    # checkin = db.relationship("SupervisorCheckin", backref="material_logs", lazy=True) # If checkin_id is added

    def calculate_replacement_date(self):
        """Calculates the expected replacement date based on material type duration."""
        if self.material_type and self.material_type.expected_duration_days:
            self.expected_replacement_date = (self.delivery_date + timedelta(days=self.material_type.expected_duration_days)).date()
        else:
            self.expected_replacement_date = None

    def __repr__(self):
        return f"<MaterialLog {self.id}: {self.quantity} of {self.material_type_id} to {self.employee_id} on {self.delivery_date}>"

# Add event listener to calculate replacement date before insert/update
from sqlalchemy import event

@event.listens_for(MaterialLog, 'before_insert')
@event.listens_for(MaterialLog, 'before_update')
def receive_before_insert_update(mapper, connection, target):
    target.calculate_replacement_date()


