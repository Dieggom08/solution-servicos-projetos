
import os
import sys
# Add project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.main import app, db
from src.models.employee import Employee
from werkzeug.security import generate_password_hash

def create_admin_user():
    with app.app_context():
        # Check if admin user already exists
        admin_email = "admin@solution.com"
        admin_username = "admin"
        admin_password = "password" # Use a more secure password in production

        existing_admin = Employee.query.filter(
            (Employee.email == admin_email) | (Employee.name == admin_username)
        ).first()

        if existing_admin:
            print(f"Admin user ({admin_username}/{admin_email}) already exists.")
            # Optionally update password if needed
            # existing_admin.set_password(admin_password)
            # db.session.commit()
            # print("Admin password updated.")
            return

        print(f"Creating admin user ({admin_username}/{admin_email})...")
        admin = Employee(
            name=admin_username,
            email=admin_email,
            role="admin" # Ensure the role is set to admin
            # Add other required fields if any, or ensure they have defaults/are nullable
        )
        admin.set_password(admin_password) # Hash the password

        try:
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully.")
        except Exception as e:
            db.session.rollback()
            print(f"Error creating admin user: {e}")

if __name__ == "__main__":
    create_admin_user()

