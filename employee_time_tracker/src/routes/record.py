
from flask import Blueprint, request, jsonify
from datetime import datetime

# Import db and models from main
from src.main import db
from src.models.time_record import TimeRecord
from src.models.employee import Employee

# Import the token_required decorator from auth blueprint
from src.routes.auth import token_required

record_bp = Blueprint("record", __name__)

# Helper function to get or create today's record for an employee
def get_or_create_today_record(employee_id):
    today_date = datetime.utcnow().date()
    record = TimeRecord.query.filter_by(employee_id=employee_id, date=today_date).first()
    if not record:
        record = TimeRecord(employee_id=employee_id, date=today_date)
        db.session.add(record)
        # No commit here, commit after update
    return record

@record_bp.route("/checkin", methods=["POST"])
@token_required
def check_in(current_user):
    record = get_or_create_today_record(current_user.id)
    if record.check_in:
        return jsonify({"message": "Check-in já realizado hoje."}), 400

    record.check_in = datetime.utcnow()
    try:
        db.session.commit()
        return jsonify({"message": "Check-in registrado com sucesso", "time": record.check_in.isoformat()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erro ao registrar check-in", "error": str(e)}), 500

@record_bp.route("/lunch/start", methods=["POST"])
@token_required
def lunch_start(current_user):
    record = get_or_create_today_record(current_user.id)
    if not record.check_in:
        return jsonify({"message": "Realize o check-in primeiro."}), 400
    if record.lunch_start:
        return jsonify({"message": "Início do almoço já registrado hoje."}), 400
    if record.check_out:
         return jsonify({"message": "Expediente já encerrado."}), 400

    record.lunch_start = datetime.utcnow()
    try:
        db.session.commit()
        return jsonify({"message": "Início do almoço registrado com sucesso", "time": record.lunch_start.isoformat()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erro ao registrar início do almoço", "error": str(e)}), 500

@record_bp.route("/lunch/end", methods=["POST"])
@token_required
def lunch_end(current_user):
    record = get_or_create_today_record(current_user.id)
    if not record.lunch_start:
        return jsonify({"message": "Registre o início do almoço primeiro."}), 400
    if record.lunch_end:
        return jsonify({"message": "Fim do almoço já registrado hoje."}), 400
    if record.check_out:
         return jsonify({"message": "Expediente já encerrado."}), 400

    record.lunch_end = datetime.utcnow()
    try:
        db.session.commit()
        return jsonify({"message": "Fim do almoço registrado com sucesso", "time": record.lunch_end.isoformat()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erro ao registrar fim do almoço", "error": str(e)}), 500

@record_bp.route("/checkout", methods=["POST"])
@token_required
def check_out(current_user):
    record = get_or_create_today_record(current_user.id)
    if not record.check_in:
        return jsonify({"message": "Realize o check-in primeiro."}), 400
    # Allow checkout even if lunch wasn't fully recorded, but maybe flag it?
    # if record.lunch_start and not record.lunch_end:
    #     return jsonify({"message": "Registre o fim do almoço primeiro."}), 400
    if record.check_out:
        return jsonify({"message": "Check-out já realizado hoje."}), 400

    record.check_out = datetime.utcnow()
    try:
        db.session.commit()
        return jsonify({"message": "Check-out registrado com sucesso", "time": record.check_out.isoformat()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erro ao registrar check-out", "error": str(e)}), 500

@record_bp.route("/status", methods=["GET"])
@token_required
def get_status(current_user):
    record = get_or_create_today_record(current_user.id)
    return jsonify({
        "employee_id": current_user.id,
        "date": record.date.isoformat(),
        "check_in": record.check_in.isoformat() if record.check_in else None,
        "lunch_start": record.lunch_start.isoformat() if record.lunch_start else None,
        "lunch_end": record.lunch_end.isoformat() if record.lunch_end else None,
        "check_out": record.check_out.isoformat() if record.check_out else None,
    })

@record_bp.route("/history", methods=["GET"])
@token_required
def get_history(current_user):
    # Add pagination later if needed
    records = TimeRecord.query.filter_by(employee_id=current_user.id).order_by(TimeRecord.date.desc()).limit(30).all()
    history = [
        {
            "id": r.id,
            "date": r.date.isoformat(),
            "check_in": r.check_in.isoformat() if r.check_in else None,
            "lunch_start": r.lunch_start.isoformat() if r.lunch_start else None,
            "lunch_end": r.lunch_end.isoformat() if r.lunch_end else None,
            "check_out": r.check_out.isoformat() if r.check_out else None,
        } for r in records
    ]
    return jsonify(history)


