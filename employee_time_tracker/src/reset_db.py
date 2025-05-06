
import os
import sys
# Add project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.main import app, db

# Import all models to ensure they are registered with SQLAlchemy
from src.models.employee import Employee
from src.models.time_record import TimeRecord
from src.models.supervisor_checkin import SupervisorCheckin
from src.models.supervisor_questionnaire import SupervisorQuestionnaireResponse
from src.models.supervisor_correction_request import SupervisorCorrectionRequest
from src.models.material import MaterialType
from src.models.material_log import MaterialLog

def reset_database():
    with app.app_context():
        print("Dropping all tables...")
        # Drop tables in reverse order of dependency if needed, or use metadata.drop_all
        # For simplicity, metadata.drop_all handles dependencies
        db.drop_all()
        print("Creating all tables...")
        db.create_all()
        print("Database has been reset.")

if __name__ == "__main__":
    reset_database()

