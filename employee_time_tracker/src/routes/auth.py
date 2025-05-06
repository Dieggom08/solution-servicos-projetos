
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt # PyJWT for token generation
import datetime
from functools import wraps
import os

# Import db and models from main - assuming db is defined in main.py
from src.main import db
from src.models.employee import Employee

auth_bp = Blueprint("auth", __name__)

# Secret key for JWT - should be in config
SECRET_KEY = os.getenv("SECRET_KEY", "your_very_secret_key_here")

# Decorator for verifying the JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({"message": "Token format is invalid!"}), 401

        if not token:
            return jsonify({"message": "Token is missing!"}), 401

        try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = Employee.query.filter_by(id=data["user_id"]).first()
            if not current_user:
                 return jsonify({"message": "User not found!"}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Token is invalid!"}), 401

        # returns the current logged in users contex to the routes
        return f(current_user, *args, **kwargs)

    return decorated

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or not data.get("username") or not data.get("password"):
        return jsonify({"message": "Username and password required"}), 400

    username = data.get("username")
    password = data.get("password")

    # Find user by username or email
    user = Employee.query.filter(
        (Employee.name == username) | (Employee.email == username)
    ).first()

    if not user:
        return jsonify({"message": "User not found"}), 401

    # Check password hash
    # Assuming password_hash is stored in the Employee model
    if user and user.password_hash and check_password_hash(user.password_hash, password):
        # Generate token
        token = jwt.encode(
            {
                "user_id": user.id,
                "role": user.role,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24), # Token expires in 24 hours
            },
            SECRET_KEY,
            algorithm="HS256",
        )

        return jsonify(
            {
                "message": "Login successful",
                "access_token": token,
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "role": user.role,
                },
            }
        )
    else:
        return jsonify({"message": "Invalid credentials"}), 401

# Example protected route
@auth_bp.route("/status", methods=["GET"])
@token_required
def status(current_user):
    return jsonify({
        "message": "Token is valid",
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "role": current_user.role,
        }
    })

# Note: Registration might be handled by admin, not a public route
# If needed, add a registration route here, potentially protected.

