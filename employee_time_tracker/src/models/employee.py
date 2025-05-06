
from src.main import db # Import db from main app in src
from datetime import datetime, date, time
from sqlalchemy.dialects.mysql import LONGTEXT # Use LONGTEXT for potentially large text fields
from werkzeug.security import generate_password_hash # To hash passwords

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Dados Pessoais
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False) # Added email field
    password_hash = db.Column(db.String(255), nullable=False) # Added password hash field
    phone_number = db.Column(db.String(20), nullable=True, unique=True) # Made nullable, password is now separate
    cpf = db.Column(db.String(14), unique=True, nullable=True) # Store formatted CPF (e.g., XXX.XXX.XXX-XX)
    rg = db.Column(db.String(20), unique=True, nullable=True)
    birth_date = db.Column(db.Date, nullable=True)
    address_street = db.Column(db.String(255), nullable=True)
    address_number = db.Column(db.String(20), nullable=True)
    address_complement = db.Column(db.String(100), nullable=True)
    address_neighborhood = db.Column(db.String(100), nullable=True)
    address_city = db.Column(db.String(100), nullable=True)
    address_state = db.Column(db.String(2), nullable=True) # UF (e.g., SP)
    address_zip = db.Column(db.String(9), nullable=True) # Store formatted CEP (e.g., XXXXX-XXX)
    marital_status = db.Column(db.String(50), nullable=True)
    dependents_info = db.Column(LONGTEXT, nullable=True) # Store JSON or text description

    # Dados Contratuais
    admission_date = db.Column(db.Date, nullable=True)
    role = db.Column(db.String(50), nullable=False, default="employee") # Added default, made non-nullable
    base_salary = db.Column(db.Float, nullable=True)
    work_schedule = db.Column(db.String(255), nullable=True) # e.g., "Seg-Sex, 08:00-17:00; Sab 08:00-12:00"
    contract_type = db.Column(db.String(50), nullable=True) # CLT, Estagiário, Temporário
    hiring_regime = db.Column(db.String(50), nullable=True) # Integral, Parcial, Home Office
    # Expected times for lateness check
    expected_arrival_time = db.Column(db.Time, nullable=True)
    expected_departure_time = db.Column(db.Time, nullable=True)
    # Add expected lunch times if needed for checks
    # expected_lunch_start_time = db.Column(db.Time, nullable=True)
    # expected_lunch_end_time = db.Column(db.Time, nullable=True)

    # Controle de Ponto e Frequência (Records are in TimeRecord model)
    # Banco de horas might need a separate model or calculation logic
    # Absences/Justifications might need a separate model

    # Gestão de Férias
    vacation_acquisition_start = db.Column(db.Date, nullable=True)
    vacation_balance_days = db.Column(db.Integer, default=0, nullable=True)
    vacation_scheduled_start = db.Column(db.Date, nullable=True)
    vacation_scheduled_end = db.Column(db.Date, nullable=True)
    # Pecuniary Abatement info could be stored elsewhere or calculated

    # 13º Salário (Usually calculated, but can store flags/notes)
    thirteenth_salary_notes = db.Column(LONGTEXT, nullable=True)

    # Benefícios
    benefits_info = db.Column(LONGTEXT, nullable=True) # Store JSON or text description (VT, VR, Health Plan, etc.)

    # Documentos Legais (Store references or flags, not the docs themselves)
    legal_docs_references = db.Column(LONGTEXT, nullable=True) # e.g., path to scanned docs, notes

    # Histórico de Avaliações e Treinamentos
    evaluation_training_history = db.Column(LONGTEXT, nullable=True) # Store JSON or text description

    # Dados para Obrigações Legais e Previdenciárias
    legal_obligations_info = db.Column(LONGTEXT, nullable=True) # Store relevant IDs or notes (INSS, FGTS, etc.)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    time_records = db.relationship("TimeRecord", backref="employee", lazy=True)
    # The relationship to MaterialLog is defined via the backref in MaterialLog model
    # No explicit relationship needed here if MaterialLog defines the backref

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # check_password method is used in auth.py via check_password_hash directly

    def __repr__(self):
        return f"<Employee {self.id}: {self.name} ({self.email})>"


