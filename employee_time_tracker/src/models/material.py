
from src.main import db # Import db from main app in src
from datetime import datetime

# Renamed class from Material to MaterialType for consistency
class MaterialType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    # Renamed for consistency with frontend/previous model
    expected_duration_days = db.Column(db.Integer, nullable=True)
    # Optional: Category for easier filtering (e.g., EPI, Limpeza, Uniforme)
    category = db.Column(db.String(50), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship removed from here - defined in MaterialLog with backref
    # logs = db.relationship("MaterialLog", backref="material_type", lazy=True)

    def __repr__(self):
        return f"<MaterialType {self.id}: {self.name}>"


