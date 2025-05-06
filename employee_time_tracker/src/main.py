
import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy # Import SQLAlchemy
from flask_cors import CORS # Import CORS

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'your_very_secret_key_here' # Change this!

# Initialize CORS - Allow all origins for development
CORS(app, resources={r"/*": {"origins": "*"}})

# Define db instance here
db = SQLAlchemy()

# Configure and initialize db with app
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USERNAME', 'root')}:{os.getenv('DB_PASSWORD', 'password')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'mydb')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Import models *after* db is defined and initialized
# Models will be imported within app context later or in blueprints

# Import blueprints
from src.routes.auth import auth_bp
from src.routes.record import record_bp
from src.routes.admin import admin_bp
from src.routes.supervisor import supervisor_bp
from src.routes.materials import materials_bp # Import materials blueprint

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth') # Changed prefix for consistency
app.register_blueprint(record_bp, url_prefix='/record') # Changed prefix for consistency
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(supervisor_bp, url_prefix="/supervisor") # Changed prefix for consistency
app.register_blueprint(materials_bp, url_prefix='/admin/materials') # Register materials blueprint under admin


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            # If index.html doesn't exist, maybe return a simple message or API docs later
            return "Welcome to the Employee Time Tracker API. Frontend not found.", 200

if __name__ == '__main__':
    # Use environment variable for port, default to 5004
    port = int(os.getenv('FLASK_PORT', 5004))
    # We need to create tables before running
    with app.app_context():
        # Import models here just before creating tables
        # This ensures db is initialized and app context is active
        from src.models.employee import Employee
        from src.models.time_record import TimeRecord
        from src.models.supervisor_checkin import SupervisorCheckin
        from src.models.supervisor_questionnaire import SupervisorQuestionnaireResponse
        from src.models.supervisor_correction_request import SupervisorCorrectionRequest
        from src.models.material import MaterialType # Corrected import name
        from src.models.material_log import MaterialLog
        db.create_all()
    app.run(host='0.0.0.0', port=port, debug=True)


