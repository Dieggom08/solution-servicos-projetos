
from flask import Blueprint, request, jsonify
from src.main import db # Import db from main app in src
from src.models.material import MaterialType # Corrected import
from src.models.material_log import MaterialLog
from src.models.employee import Employee # To verify employee exists
from datetime import datetime, timedelta # Added timedelta

# Define the Blueprint
materials_bp = Blueprint("materials", __name__)

# TODO: Add authentication/authorization (e.g., only Admin can manage)

# --- Material Type Management --- #

@materials_bp.route("/types", methods=["POST"])
def add_material_type():
    """
    Adds a new type of material to the system.
    JSON Body:
        name (str, required): Name of the material type.
        description (str, optional): Description.
        expected_duration_days (int, optional): Expected duration in days.
        category (str, optional): Category.
    """
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({"error": "O nome do tipo de material é obrigatório"}), 400

    name = data["name"]

    # Check if material type already exists
    if MaterialType.query.filter_by(name=name).first():
        return jsonify({"error": "Tipo de material já existe"}), 409

    try:
        new_material_type = MaterialType(
            name=name,
            description=data.get("description"),
            expected_duration_days=data.get("expected_duration_days"), # Corrected field name
            category=data.get("category")
        )
        db.session.add(new_material_type)
        db.session.commit()
        return jsonify({"message": "Tipo de material adicionado com sucesso", "material_type_id": new_material_type.id}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error adding material type: {e}")
        return jsonify({"error": f"Erro ao adicionar tipo de material: {e}"}), 500

@materials_bp.route("/types/<int:type_id>", methods=["PUT"])
def update_material_type(type_id):
    """Updates an existing material type."""
    material_type = MaterialType.query.get_or_404(type_id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados não fornecidos"}), 400

    try:
        material_type.name = data.get("name", material_type.name)
        material_type.description = data.get("description", material_type.description)
        material_type.expected_duration_days = data.get("expected_duration_days", material_type.expected_duration_days)
        material_type.category = data.get("category", material_type.category)
        db.session.commit()
        return jsonify({"message": "Tipo de material atualizado com sucesso"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating material type: {e}")
        return jsonify({"error": f"Erro ao atualizar tipo de material: {e}"}), 500

@materials_bp.route("/types/<int:type_id>", methods=["DELETE"])
def delete_material_type(type_id):
    """Deletes a material type."""
    material_type = MaterialType.query.get_or_404(type_id)
    try:
        # Consider implications: what happens to logs referencing this type?
        # Maybe prevent deletion if logs exist, or handle logs (e.g., set type_id to null if allowed).
        # For now, just delete.
        db.session.delete(material_type)
        db.session.commit()
        return jsonify({"message": "Tipo de material excluído com sucesso"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting material type: {e}")
        # Check for integrity errors (e.g., foreign key constraint)
        if "foreign key constraint" in str(e).lower():
             return jsonify({"error": "Não é possível excluir: existem registros de entrega associados a este tipo de material."}), 409
        return jsonify({"error": f"Erro ao excluir tipo de material: {e}"}), 500


@materials_bp.route("/types", methods=["GET"])
def list_material_types():
    """Lists all available material types."""
    try:
        material_types = MaterialType.query.order_by(MaterialType.name).all()
        return jsonify([{
            "id": mat.id,
            "name": mat.name,
            "description": mat.description,
            "expected_duration_days": mat.expected_duration_days, # Corrected field name
            "category": mat.category
        } for mat in material_types]), 200
    except Exception as e:
        print(f"Error listing material types: {e}")
        return jsonify({"error": f"Erro ao listar tipos de material: {e}"}), 500

# --- Material Log Management --- #

@materials_bp.route("/logs", methods=["POST"])
def log_material_delivery():
    """
    Logs the delivery of a material to an employee.
    JSON Body:
        material_type_id (int, required): ID of the material type delivered.
        employee_id (int, required): ID of the employee receiving the material.
        quantity (int, optional, default=1): Quantity delivered.
        photo_url (str, optional): URL of photo confirming delivery/usage.
        notes (str, optional): Notes about the delivery.
        delivery_date (str, optional, format YYYY-MM-DD): Defaults to today.
    """
    data = request.get_json()
    if not data or not data.get("material_type_id") or not data.get("employee_id"):
        return jsonify({"error": "material_type_id e employee_id são obrigatórios"}), 400

    material_type_id = data["material_type_id"]
    employee_id = data["employee_id"]

    # Verify material type exists
    material_type = MaterialType.query.get(material_type_id)
    if not material_type:
        return jsonify({"error": "Tipo de material não encontrado"}), 404

    # Verify employee exists
    employee = Employee.query.get(employee_id)
    if not employee:
        return jsonify({"error": "Funcionário não encontrado"}), 404

    delivery_date_str = data.get("delivery_date")
    delivery_date = datetime.utcnow().date() # Use date part only by default
    if delivery_date_str:
        try:
            # Corrected syntax for strptime
            delivery_date = datetime.strptime(delivery_date_str, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Formato inválido para delivery_date. Use YYYY-MM-DD"}), 400

    try:
        new_log = MaterialLog(
            material_type_id=material_type_id,
            employee_id=employee_id,
            quantity=data.get("quantity", 1),
            photo_url=data.get("photo_url"), # Placeholder: Upload logic needed
            notes=data.get("notes"),
            delivery_date=datetime.combine(delivery_date, datetime.min.time()) # Store as datetime for consistency?
            # checkin_id=data.get("checkin_id") # Add if linking to checkin
        )
        # The replacement date calculation happens automatically via event listener
        db.session.add(new_log)
        db.session.commit()
        return jsonify({"message": "Entrega de material registrada com sucesso", "log_id": new_log.id}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error logging material delivery: {e}")
        return jsonify({"error": f"Erro ao registrar entrega de material: {e}"}), 500

@materials_bp.route("/logs", methods=["GET"])
def list_material_logs():
    """
    Lists material delivery logs.
    Query Parameters:
        employee_id (int, optional): Filter by employee ID.
        material_type_id (int, optional): Filter by material type ID.
        start_date (str, optional, YYYY-MM-DD): Filter by delivery start date.
        end_date (str, optional, YYYY-MM-DD): Filter by delivery end date.
    """
    query = MaterialLog.query.join(MaterialType).join(Employee) # Join for easy access to names

    employee_id = request.args.get("employee_id")
    if employee_id:
        try:
            query = query.filter(MaterialLog.employee_id == int(employee_id))
        except ValueError:
            return jsonify({"error": "employee_id inválido"}), 400

    material_type_id = request.args.get("material_type_id")
    if material_type_id:
        try:
            query = query.filter(MaterialLog.material_type_id == int(material_type_id))
        except ValueError:
            return jsonify({"error": "material_type_id inválido"}), 400

    start_date_str = request.args.get("start_date")
    if start_date_str:
        try:
            # Corrected syntax for strptime
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            query = query.filter(MaterialLog.delivery_date >= datetime.combine(start_date, datetime.min.time()))
        except ValueError:
            return jsonify({"error": "Formato inválido para start_date. Use YYYY-MM-DD"}), 400

    end_date_str = request.args.get("end_date")
    if end_date_str:
        try:
            # Corrected syntax for strptime
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            # Add 1 day to end_date to include the whole day
            query = query.filter(MaterialLog.delivery_date < datetime.combine(end_date + timedelta(days=1), datetime.min.time()))
        except ValueError:
            return jsonify({"error": "Formato inválido para end_date. Use YYYY-MM-DD"}), 400

    try:
        logs = query.order_by(MaterialLog.delivery_date.desc()).all()
        return jsonify([{
            "id": log.id,
            "material_type_id": log.material_type_id,
            "material_type_name": log.material_type.name, # Include name via relationship
            "employee_id": log.employee_id,
            "employee_name": log.employee.name, # Include name via relationship
            "delivery_date": log.delivery_date.isoformat(),
            "quantity": log.quantity,
            "photo_url": log.photo_url,
            "notes": log.notes,
            "expected_replacement_date": log.expected_replacement_date.isoformat() if log.expected_replacement_date else None
        } for log in logs]), 200
    except Exception as e:
        db.session.rollback() # Rollback in case of error during serialization
        print(f"Error listing material logs: {e}")
        return jsonify({"error": f"Erro ao listar registros de material: {e}"}), 500


