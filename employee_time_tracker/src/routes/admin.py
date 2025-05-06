
from flask import Blueprint, request, jsonify, make_response, send_file
from src.main import db # Import db from main app in src
from src.models.employee import Employee
from src.models.time_record import TimeRecord
from sqlalchemy import and_
from sqlalchemy.orm import joinedload
from datetime import datetime, time, timedelta
import io
import os # For logo path

# Import PDF generation utility
from src.utils.pdf_generator import generate_pdf_report
# Import calculation utilities
from src.utils.hours_calculator import calculate_worked_hours, determine_absences

# Define the Blueprint
admin_bp = Blueprint("admin", __name__)

# TODO: Add authentication/authorization (e.g., only Admin role)

# --- Employee Management --- #

@admin_bp.route("/employees", methods=["POST"])
def add_employee():
    """Adds a new employee."""
    data = request.get_json()
    # Basic validation - ensure required fields are present
    required_fields = ["name", "email", "password", "role"]
    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": "Campos obrigatórios ausentes (nome, email, senha, cargo)"}), 400

    # Check if email already exists
    if Employee.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email já cadastrado"}), 409

    # Create new employee instance
    new_employee = Employee(
        name=data["name"],
        email=data["email"],
        role=data["role"],
        phone_number=data.get("phone_number"),
        cpf=data.get("cpf"),
        rg=data.get("rg"),
        birth_date=datetime.strptime(data["birth_date"], "%Y-%m-%d").date() if data.get("birth_date") else None,
        address_street=data.get("address_street"),
        address_number=data.get("address_number"),
        address_complement=data.get("address_complement"),
        address_neighborhood=data.get("address_neighborhood"),
        address_city=data.get("address_city"),
        address_state=data.get("address_state"),
        address_zip=data.get("address_zip"),
        marital_status=data.get("marital_status"),
        dependents_info=data.get("dependents_info"),
        admission_date=datetime.strptime(data["admission_date"], "%Y-%m-%d").date() if data.get("admission_date") else None,
        base_salary=data.get("base_salary"),
        work_schedule=data.get("work_schedule"),
        contract_type=data.get("contract_type"),
        hiring_regime=data.get("hiring_regime"),
        expected_arrival_time=datetime.strptime(data["expected_arrival_time"], "%H:%M").time() if data.get("expected_arrival_time") else None,
        expected_departure_time=datetime.strptime(data["expected_departure_time"], "%H:%M").time() if data.get("expected_departure_time") else None,
        vacation_acquisition_start=datetime.strptime(data["vacation_acquisition_start"], "%Y-%m-%d").date() if data.get("vacation_acquisition_start") else None,
        vacation_balance_days=data.get("vacation_balance_days", 0),
        thirteenth_salary_notes=data.get("thirteenth_salary_notes"),
        benefits_info=data.get("benefits_info"),
        legal_docs_references=data.get("legal_docs_references"),
        evaluation_training_history=data.get("evaluation_training_history"),
        legal_obligations_info=data.get("legal_obligations_info")
        # Removed fields not present in the final Employee model: job_title, department, work_shift, hourly_rate, bank_details, emergency_contact_name, emergency_contact_phone, status
    )
    new_employee.set_password(data["password"]) # Hash the password

    try:
        db.session.add(new_employee)
        db.session.commit()
        # Return only necessary info, avoid returning password hash
        return jsonify({
            "message": "Funcionário adicionado com sucesso",
            "employee": {
                "id": new_employee.id,
                "name": new_employee.name,
                "email": new_employee.email,
                "role": new_employee.role
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error adding employee: {e}")
        return jsonify({"error": f"Erro ao adicionar funcionário: {e}"}), 500

@admin_bp.route("/employees", methods=["GET"])
def list_employees():
    """Lists all employees."""
    try:
        employees = Employee.query.order_by(Employee.name).all()
        employee_list = []
        for emp in employees:
            # Construct full address string
            address_parts = [
                emp.address_street,
                emp.address_number,
                emp.address_complement,
                emp.address_neighborhood,
                emp.address_city,
                emp.address_state,
                emp.address_zip
            ]
            full_address = ", ".join(part for part in address_parts if part) # Join non-empty parts

            employee_list.append({
                "id": emp.id,
                "name": emp.name,
                "email": emp.email,
                "phone_number": emp.phone_number,
                "role": emp.role,
                "cpf": emp.cpf,
                "rg": emp.rg,
                "birth_date": emp.birth_date.isoformat() if emp.birth_date else None,
                "address": full_address, # Use the constructed full address
                "address_street": emp.address_street,
                "address_number": emp.address_number,
                "address_complement": emp.address_complement,
                "address_neighborhood": emp.address_neighborhood,
                "address_city": emp.address_city,
                "address_state": emp.address_state,
                "address_zip": emp.address_zip,
                "marital_status": emp.marital_status,
                "dependents_info": emp.dependents_info,
                "admission_date": emp.admission_date.isoformat() if emp.admission_date else None,
                "base_salary": emp.base_salary,
                "work_schedule": emp.work_schedule,
                "contract_type": emp.contract_type,
                "hiring_regime": emp.hiring_regime,
                "expected_arrival_time": emp.expected_arrival_time.strftime("%H:%M") if emp.expected_arrival_time else None,
                "expected_departure_time": emp.expected_departure_time.strftime("%H:%M") if emp.expected_departure_time else None,
                "vacation_acquisition_start": emp.vacation_acquisition_start.isoformat() if emp.vacation_acquisition_start else None,
                "vacation_balance_days": emp.vacation_balance_days,
                "thirteenth_salary_notes": emp.thirteenth_salary_notes,
                "benefits_info": emp.benefits_info,
                "legal_docs_references": emp.legal_docs_references,
                "evaluation_training_history": emp.evaluation_training_history,
                "legal_obligations_info": emp.legal_obligations_info,
                "created_at": emp.created_at.isoformat() if emp.created_at else None,
                "updated_at": emp.updated_at.isoformat() if emp.updated_at else None
                # Removed fields not present in the final Employee model: job_title, department, work_shift, hourly_rate, bank_details, emergency_contact_name, emergency_contact_phone, status
            })
        return jsonify(employee_list), 200
    except Exception as e:
        print(f"Error listing employees: {e}")
        return jsonify({"error": f"Erro ao listar funcionários: {e}"}), 500

# TODO: Add routes for updating and deleting employees

# --- Time Record Viewing --- #

@admin_bp.route("/time-records", methods=["GET"])
def get_time_records():
    """Fetches time records, optionally filtered by employee and date range."""
    employee_id = request.args.get("employee_id")
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")

    query = TimeRecord.query.options(joinedload(TimeRecord.employee))

    if employee_id:
        try:
            query = query.filter(TimeRecord.employee_id == int(employee_id))
        except ValueError:
            return jsonify({"error": "employee_id inválido"}), 400

    try:
        if start_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            query = query.filter(TimeRecord.timestamp >= datetime.combine(start_date, time.min))
        if end_date_str:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            query = query.filter(TimeRecord.timestamp <= datetime.combine(end_date, time.max))
    except ValueError:
        return jsonify({"error": "Formato de data inválido. Use YYYY-MM-DD"}), 400

    try:
        records = query.order_by(TimeRecord.timestamp.desc()).all()
        return jsonify([{
            "id": record.id,
            "employee_id": record.employee_id,
            "employee_name": record.employee.name, # Requires loading relationship
            "timestamp": record.timestamp.isoformat(),
            "record_type": record.record_type,
            "latitude": record.latitude,
            "longitude": record.longitude,
            "photo_url": record.photo_url
        } for record in records]), 200
    except Exception as e:
        print(f"Error fetching time records: {e}")
        return jsonify({"error": f"Erro ao buscar registros de ponto: {e}"}), 500

# --- Lateness Report --- #

# Helper function (can be moved to utils)
def get_lateness_data(start_date, end_date, employee_id=None):
    # Fetch employees to get their specific expected arrival times
    employee_query = Employee.query
    if employee_id:
        employee_query = employee_query.filter(Employee.id == employee_id)
    employees = employee_query.all()
    employee_arrival_times = {emp.id: emp.expected_arrival_time for emp in employees if emp.expected_arrival_time}

    # Allow a grace period (e.g., 5 minutes)
    grace_period = timedelta(minutes=5)

    query = TimeRecord.query.filter(
        TimeRecord.record_type == "arrival",
        TimeRecord.timestamp >= datetime.combine(start_date, time.min),
        TimeRecord.timestamp <= datetime.combine(end_date, time.max)
    ).options(joinedload(TimeRecord.employee))

    if employee_id:
        query = query.filter(TimeRecord.employee_id == employee_id)

    all_arrivals = query.order_by(TimeRecord.timestamp).all()

    report_data = []
    for record in all_arrivals:
        expected_arrival_time = employee_arrival_times.get(record.employee_id)
        if not expected_arrival_time:
            continue # Skip if employee has no expected arrival time set

        expected_arrival_with_grace = (datetime.combine(datetime.min, expected_arrival_time) + grace_period).time()
        arrival_dt = record.timestamp

        # Check if arrival time is actually later than grace period time
        if arrival_dt.time() > expected_arrival_with_grace:
            expected_dt_today = datetime.combine(arrival_dt.date(), expected_arrival_time)
            lateness = arrival_dt - expected_dt_today
            if lateness > timedelta(0):
                report_data.append({
                    "employee_name": record.employee.name,
                    "date": arrival_dt.strftime("%Y-%m-%d"),
                    "arrival_time": arrival_dt.strftime("%H:%M:%S"),
                    "lateness_minutes": int(lateness.total_seconds() / 60),
                    "expected_arrival_time": expected_arrival_time.strftime("%H:%M:%S")
                })
    return report_data

@admin_bp.route("/reports/lateness", methods=["GET"])
def report_lateness():
    """Generates a lateness report, optionally filtered by date and employee.
       Accepts 'format=pdf' query parameter for PDF download.
    """
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")
    employee_id = request.args.get("employee_id")
    report_format = request.args.get("format") # Check for pdf format request

    # Default to the current month if dates are not provided
    today = datetime.utcnow().date()
    if not start_date_str:
        start_date = today.replace(day=1)
    else:
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Formato inválido para start_date. Use YYYY-MM-DD"}), 400

    if not end_date_str:
        # Find the last day of the start_date month
        next_month = start_date.replace(day=28) + timedelta(days=4)
        end_date = next_month - timedelta(days=next_month.day)
    else:
        try:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Formato inválido para end_date. Use YYYY-MM-DD"}), 400

    if employee_id:
        try:
            employee_id = int(employee_id)
        except ValueError:
            return jsonify({"error": "employee_id inválido"}), 400

    try:
        lateness_records = get_lateness_data(start_date, end_date, employee_id)

        # If PDF format is requested
        if report_format and report_format.lower() == "pdf":
            logo_file_path = "/home/ubuntu/upload/logo_refinada_1.png" # Use refined logo
            pdf_data = {
                "records": lateness_records,
                "start_date": start_date.strftime("%d/%m/%Y"),
                "end_date": end_date.strftime("%d/%m/%Y")
            }
            pdf_bytes = generate_pdf_report("report_lateness.html", pdf_data, logo_path=logo_file_path)

            if pdf_bytes:
                response = make_response(pdf_bytes)
                response.headers["Content-Type"] = "application/pdf"
                response.headers["Content-Disposition"] = f"attachment; filename=relatorio_atrasos_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.pdf"
                return response
            else:
                return jsonify({"error": "Falha ao gerar relatório PDF"}), 500
        else:
            # Return JSON data for web display
            return jsonify(lateness_records), 200

    except Exception as e:
        print(f"Error generating lateness report: {e}")
        return jsonify({"error": f"Erro ao gerar relatório de atrasos: {e}"}), 500

# --- Hours Worked Report --- #

@admin_bp.route("/reports/hours-worked", methods=["GET"])
def report_hours_worked():
    """Generates a worked hours report for a specific employee and date range.
       Accepts 'format=pdf' query parameter for PDF download.
    """
    employee_id = request.args.get("employee_id")
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")
    report_format = request.args.get("format")

    if not employee_id:
        return jsonify({"error": "employee_id é obrigatório para este relatório"}), 400

    try:
        employee_id = int(employee_id)
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({"error": "Funcionário não encontrado"}), 404
    except ValueError:
        return jsonify({"error": "employee_id inválido"}), 400

    # Default to the current month if dates are not provided
    today = datetime.utcnow().date()
    if not start_date_str:
        start_date = today.replace(day=1)
    else:
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Formato inválido para start_date. Use YYYY-MM-DD"}), 400

    if not end_date_str:
        next_month = start_date.replace(day=28) + timedelta(days=4)
        end_date = next_month - timedelta(days=next_month.day)
    else:
        try:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Formato inválido para end_date. Use YYYY-MM-DD"}), 400

    try:
        # Fetch records for the employee in the date range
        records = TimeRecord.query.filter(
            TimeRecord.employee_id == employee_id,
            TimeRecord.timestamp >= datetime.combine(start_date, time.min),
            TimeRecord.timestamp <= datetime.combine(end_date, time.max)
        ).order_by(TimeRecord.timestamp).all()

        weekly_summaries = calculate_worked_hours(records)

        if report_format and report_format.lower() == "pdf":
            logo_file_path = "/home/ubuntu/upload/logo_refinada_1.png" # Use refined logo
            pdf_data = {
                "weekly_summaries": weekly_summaries,
                "employee_name": employee.name,
                "start_date": start_date.strftime("%d/%m/%Y"),
                "end_date": end_date.strftime("%d/%m/%Y")
            }
            pdf_bytes = generate_pdf_report("report_hours_worked.html", pdf_data, logo_path=logo_file_path)

            if pdf_bytes:
                response = make_response(pdf_bytes)
                response.headers["Content-Type"] = "application/pdf"
                response.headers["Content-Disposition"] = f"attachment; filename=relatorio_horas_{employee.name.replace(' ','_')}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.pdf"
                return response
            else:
                return jsonify({"error": "Falha ao gerar relatório PDF"}), 500
        else:
            return jsonify(weekly_summaries), 200

    except Exception as e:
        print(f"Error generating hours worked report: {e}")
        return jsonify({"error": f"Erro ao gerar relatório de horas trabalhadas: {e}"}), 500

# --- Absences Report --- #

@admin_bp.route("/reports/absences", methods=["GET"])
def report_absences():
    """Generates an absences report, optionally filtered by date and employee.
       Accepts 'format=pdf' query parameter for PDF download.
    """
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")
    employee_id = request.args.get("employee_id")
    report_format = request.args.get("format")

    # Default to the current month if dates are not provided
    today = datetime.utcnow().date()
    if not start_date_str:
        start_date = today.replace(day=1)
    else:
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Formato inválido para start_date. Use YYYY-MM-DD"}), 400

    if not end_date_str:
        next_month = start_date.replace(day=28) + timedelta(days=4)
        end_date = next_month - timedelta(days=next_month.day)
    else:
        try:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Formato inválido para end_date. Use YYYY-MM-DD"}), 400

    try:
        # Fetch relevant employees (active)
        # Assuming Employee model has a status field, otherwise adjust filter
        employee_query = Employee.query # .filter(Employee.status == 'active')
        if employee_id:
            try:
                employee_query = employee_query.filter(Employee.id == int(employee_id))
            except ValueError:
                return jsonify({"error": "employee_id inválido"}), 400
        employees = employee_query.all()

        # Fetch all records within the date range (potentially optimize later)
        records = TimeRecord.query.filter(
            TimeRecord.timestamp >= datetime.combine(start_date, time.min),
            TimeRecord.timestamp <= datetime.combine(end_date, time.max)
        ).all()

        absences_data = determine_absences(start_date, end_date, employees, records)

        if report_format and report_format.lower() == "pdf":
            logo_file_path = "/home/ubuntu/upload/logo_refinada_1.png" # Use refined logo
            pdf_data = {
                "absences": absences_data,
                "start_date": start_date.strftime("%d/%m/%Y"),
                "end_date": end_date.strftime("%d/%m/%Y")
            }
            pdf_bytes = generate_pdf_report("report_absences.html", pdf_data, logo_path=logo_file_path)

            if pdf_bytes:
                response = make_response(pdf_bytes)
                response.headers["Content-Type"] = "application/pdf"
                response.headers["Content-Disposition"] = f"attachment; filename=relatorio_ausencias_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.pdf"
                return response
            else:
                return jsonify({"error": "Falha ao gerar relatório PDF"}), 500
        else:
            return jsonify(absences_data), 200

    except Exception as e:
        print(f"Error generating absences report: {e}")
        return jsonify({"error": f"Erro ao gerar relatório de ausências: {e}"}), 500

