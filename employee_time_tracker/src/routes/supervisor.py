
from flask import Blueprint, request, jsonify
from src.main import db # Import db from main app in src
from src.models.employee import Employee
from src.models.supervisor_checkin import SupervisorCheckin
from src.models.supervisor_questionnaire import SupervisorQuestionnaireResponse
from src.models.supervisor_correction_request import SupervisorCorrectionRequest
from src.models.time_record import TimeRecord # Needed for correction requests
from datetime import datetime
import os # For potential file handling

# Define the Blueprint
supervisor_bp = Blueprint("supervisor", __name__)

# TODO: Add authentication/authorization to ensure only supervisors access these routes
# This would typically involve checking the user's role from a session or token

# --- Supervisor Check-in --- #

@supervisor_bp.route("/checkin", methods=["POST"])
def supervisor_checkin():
    """
    Records a supervisor check-in event.
    Requires supervisor_id, photo_url, and optionally location data.
    JSON Body:
        supervisor_id (int, required): ID of the supervising employee.
        photo_url (str, required): URL of the uploaded check-in photo.
        latitude (float, optional): Latitude of check-in location.
        longitude (float, optional): Longitude of check-in location.
        location_name (str, optional): Name of the location (e.g., Condominium Name).
    """
    data = request.get_json()

    if not data or not data.get("supervisor_id") or not data.get("photo_url"):
        return jsonify({"error": "supervisor_id e photo_url são obrigatórios"}), 400

    supervisor_id = data["supervisor_id"]
    photo_url = data["photo_url"]
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    location_name = data.get("location_name")

    # Verify supervisor exists and IS a supervisor
    supervisor = Employee.query.get(supervisor_id)
    if not supervisor:
        return jsonify({"error": "Supervisor não encontrado"}), 404
    # Add role check if implemented in Employee model
    # if supervisor.role != 'Supervisor':
    #     return jsonify({"error": "Funcionário não é um supervisor"}), 403

    try:
        new_checkin = SupervisorCheckin(
            supervisor_id=supervisor_id,
            photo_url=photo_url,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
            timestamp=datetime.utcnow() # Record time on server
        )
        db.session.add(new_checkin)
        db.session.commit()
        return jsonify({"message": "Check-in do supervisor registrado com sucesso", "checkin_id": new_checkin.id}), 201

    except Exception as e:
        db.session.rollback()
        print(f"Error recording supervisor check-in: {e}")
        return jsonify({"error": f"Erro ao registrar check-in: {e}"}), 500

# --- Supervisor Questionnaire --- #

@supervisor_bp.route("/questionnaire", methods=["POST"])
def submit_questionnaire():
    """
    Submits a supervisor's questionnaire response.
    JSON Body:
        supervisor_id (int, required): ID of the supervising employee.
        checkin_id (int, optional): ID of the related check-in.
        strengths_text (str, optional): Text about service strengths.
        strengths_photo_url (str, optional): URL of photo illustrating strengths.
        improvements_text (str, optional): Text about needed improvements.
        employee_wellbeing_text (str, optional): Text about employee wellbeing.
        observations_text (str, optional): General observations.
    """
    data = request.get_json()

    if not data or not data.get("supervisor_id"):
        return jsonify({"error": "supervisor_id é obrigatório"}), 400

    supervisor_id = data["supervisor_id"]

    # Verify supervisor exists
    supervisor = Employee.query.get(supervisor_id)
    if not supervisor:
        return jsonify({"error": "Supervisor não encontrado"}), 404
    # Add role check if implemented
    # if supervisor.role != 'Supervisor':
    #     return jsonify({"error": "Funcionário não é um supervisor"}), 403

    # Verify optional checkin_id if provided
    checkin_id = data.get("checkin_id")
    if checkin_id and not SupervisorCheckin.query.get(checkin_id):
        return jsonify({"error": "Check-in ID inválido"}), 404

    try:
        new_response = SupervisorQuestionnaireResponse(
            supervisor_id=supervisor_id,
            checkin_id=checkin_id,
            strengths_text=data.get("strengths_text"),
            strengths_photo_url=data.get("strengths_photo_url"), # Placeholder: Upload logic needed
            improvements_text=data.get("improvements_text"),
            employee_wellbeing_text=data.get("employee_wellbeing_text"),
            observations_text=data.get("observations_text"),
            timestamp=datetime.utcnow()
        )
        db.session.add(new_response)
        db.session.commit()
        return jsonify({"message": "Resposta do questionário registrada com sucesso", "response_id": new_response.id}), 201

    except Exception as e:
        db.session.rollback()
        print(f"Error submitting questionnaire: {e}")
        return jsonify({"error": f"Erro ao registrar resposta do questionário: {e}"}), 500

# --- Supervisor Correction Requests --- #

@supervisor_bp.route("/correction-requests", methods=["POST"])
def submit_correction_request():
    """
    Submits a request to correct an employee's time record or justify an absence.
    JSON Body:
        supervisor_id (int, required): ID of the supervising employee.
        employee_id (int, required): ID of the employee whose record needs correction.
        time_record_id (int, optional): ID of the specific time record to correct.
        requested_change_type (str, required): Type of change (e.g., "arrival_time", "absence_justification").
        original_value (str, optional): Original time or status being corrected.
        requested_value (str, required): New time (HH:MM) or justification text.
        reason (str, required): Reason for the correction request.
    """
    data = request.get_json()

    required_fields = ["supervisor_id", "employee_id", "requested_change_type", "requested_value", "reason"]
    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": "Campos obrigatórios ausentes: supervisor_id, employee_id, requested_change_type, requested_value, reason"}), 400

    supervisor_id = data["supervisor_id"]
    employee_id = data["employee_id"]
    time_record_id = data.get("time_record_id")

    # Verify supervisor exists
    supervisor = Employee.query.get(supervisor_id)
    if not supervisor:
        return jsonify({"error": "Supervisor não encontrado"}), 404
    # Add role check
    # if supervisor.role != 'Supervisor':
    #     return jsonify({"error": "Funcionário não é um supervisor"}), 403

    # Verify employee exists
    employee = Employee.query.get(employee_id)
    if not employee:
        return jsonify({"error": "Funcionário alvo não encontrado"}), 404

    # Verify time_record exists if provided
    if time_record_id and not TimeRecord.query.get(time_record_id):
         return jsonify({"error": "Registro de ponto ID inválido"}), 404

    try:
        new_request = SupervisorCorrectionRequest(
            supervisor_id=supervisor_id,
            employee_id=employee_id,
            time_record_id=time_record_id,
            requested_change_type=data["requested_change_type"],
            original_value=data.get("original_value"),
            requested_value=data["requested_value"],
            reason=data["reason"],
            request_timestamp=datetime.utcnow(),
            status="pending" # Default status
        )
        db.session.add(new_request)
        db.session.commit()
        return jsonify({"message": "Solicitação de correção enviada com sucesso", "request_id": new_request.id}), 201

    except Exception as e:
        db.session.rollback()
        print(f"Error submitting correction request: {e}")
        return jsonify({"error": f"Erro ao enviar solicitação de correção: {e}"}), 500

# TODO: Add GET routes for supervisors to view their own requests/responses?
# TODO: Add routes for Admins to view/approve/reject correction requests.

