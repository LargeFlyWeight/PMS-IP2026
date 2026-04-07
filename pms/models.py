import enum
from datetime import datetime, date, time
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from .extensions import db


class LeaveType(enum.Enum):
    VACATION = "Vacation"
    SICK_LEAVE = "Sick leave"
    PERSONAL_LEAVE = "Personal leave"


class LeaveStatus(enum.Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"


class Company(db.Model):
    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(200), nullable=False)

    departments = db.relationship("Department", back_populates="company", cascade="all, delete-orphan")

    def get_departments(self):
        return list(self.departments)


class Department(db.Model):
    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(50), nullable=True)

    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=True)

    company = db.relationship("Company", back_populates="departments")
    employees = db.relationship(
        "Employee",
        back_populates="department",
        foreign_keys="Employee.department_id",
    )
    manager = db.relationship("Employee", foreign_keys=[manager_id], post_update=True)

    def get_employees(self):
        return list(self.employees)

    def get_manager(self):
        return self.manager


class Position(db.Model):
    __tablename__ = "positions"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    salary_grade = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(300), nullable=True)

    employees = db.relationship("Employee", back_populates="position")

    def get_employees(self):
        return list(self.employees)


class Employee(UserMixin, db.Model):
    """Base class for every system user. Manager and Administrator inherit from it."""
    __tablename__ = "employees"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), unique=True, nullable=False)
    _password_hash = db.Column("password_hash", db.String(255), nullable=False)

    name = db.Column(db.String(60), nullable=False)
    surname = db.Column(db.String(60), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=True)
    _email = db.Column("email", db.String(120), unique=True, nullable=False)
    _phone_number = db.Column("phone_number", db.String(30), nullable=True)

    role = db.Column(db.String(20), nullable=False)

    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=True)
    position_id = db.Column(db.Integer, db.ForeignKey("positions.id"), nullable=True)

    department = db.relationship("Department", back_populates="employees", foreign_keys=[department_id])
    position = db.relationship("Position", back_populates="employees")

    leave_requests = db.relationship("LeaveRequest", back_populates="employee", cascade="all, delete-orphan", foreign_keys="LeaveRequest.employee_id")
    attendance_records = db.relationship("AttendanceRecord", back_populates="employee", cascade="all, delete-orphan")
    transfers = db.relationship("Transfer", back_populates="employee", cascade="all, delete-orphan")
    position_changes = db.relationship("PositionChange", back_populates="employee", cascade="all, delete-orphan")

    __mapper_args__ = {
        "polymorphic_on": role,
        "polymorphic_identity": "employee",
    }

    # encapsulation: use properties so external code does not touch raw columns
    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        if "@" not in value or "." not in value:
            raise ValueError("Invalid email format")
        self._email = value

    @property
    def phone_number(self):
        return self._phone_number

    @phone_number.setter
    def phone_number(self, value):
        if value and not all(c.isdigit() or c in "+ -()" for c in value):
            raise ValueError("Invalid phone format")
        self._phone_number = value

    def set_password(self, raw_password):
        self._password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self._password_hash, raw_password)

    @property
    def full_name(self):
        return f"{self.name} {self.surname}"

    def update_contact_details(self, email, phone):
        self.email = email
        self.phone_number = phone

    def can_view_employee(self, other):
        return other.id == self.id

    def can_manage_department(self, department):
        return False

    # polymorphic hook used by LeaveService
    def auto_approve_leave(self):
        return False

    def supervisor(self):
        """Return the user who has to approve this user's leave (or None)."""
        if self.department and self.department.manager and self.department.manager.id != self.id:
            return self.department.manager
        # if employee is not under any manager — fall back to any administrator
        admin = db.session.query(Administrator).first()
        return admin


class Manager(Employee):
    __mapper_args__ = {"polymorphic_identity": "manager"}

    def can_view_employee(self, other):
        if other.id == self.id:
            return True
        return other.department_id is not None and other.department_id == self.department_id

    def can_manage_department(self, department):
        return department is not None and department.id == self.department_id

    def supervisor(self):
        admin = db.session.query(Administrator).first()
        return admin


class Administrator(Manager):
    __mapper_args__ = {"polymorphic_identity": "administrator"}

    def can_view_employee(self, other):
        return True

    def can_manage_department(self, department):
        return True

    def auto_approve_leave(self):
        return True

    def supervisor(self):
        return None  # admin has no supervisor


class Transfer(db.Model):
    __tablename__ = "transfers"

    id = db.Column(db.Integer, primary_key=True)
    date_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)
    source_department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=False)
    destination_department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=False)

    employee = db.relationship("Employee", back_populates="transfers")
    source_department = db.relationship("Department", foreign_keys=[source_department_id])
    destination_department = db.relationship("Department", foreign_keys=[destination_department_id])

    def get_source_department(self):
        return self.source_department

    def get_destination_department(self):
        return self.destination_department


class PositionChange(db.Model):
    __tablename__ = "position_changes"

    id = db.Column(db.Integer, primary_key=True)
    date_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)
    previous_position_id = db.Column(db.Integer, db.ForeignKey("positions.id"), nullable=False)
    new_position_id = db.Column(db.Integer, db.ForeignKey("positions.id"), nullable=False)
    reason = db.Column(db.String(300), nullable=False)

    employee = db.relationship("Employee", back_populates="position_changes")
    previous_position = db.relationship("Position", foreign_keys=[previous_position_id])
    new_position = db.relationship("Position", foreign_keys=[new_position_id])

    def get_previous_position(self):
        return self.previous_position

    def get_new_position(self):
        return self.new_position


class LeaveRequest(db.Model):
    __tablename__ = "leave_requests"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)
    type = db.Column(db.Enum(LeaveType), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    date_of_request = db.Column(db.Date, nullable=False, default=date.today)
    reason = db.Column(db.String(300), nullable=False)
    status = db.Column(db.Enum(LeaveStatus), nullable=False, default=LeaveStatus.PENDING)
    supervisor_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=True)

    employee = db.relationship("Employee", back_populates="leave_requests", foreign_keys=[employee_id])
    supervisor = db.relationship("Employee", foreign_keys=[supervisor_id])

    def approve(self):
        self.status = LeaveStatus.APPROVED

    def reject(self):
        self.status = LeaveStatus.REJECTED


class AttendanceRecord(db.Model):
    __tablename__ = "attendance_records"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    lunch_break = db.Column(db.Integer, nullable=False, default=0)
    finish_time = db.Column(db.Time, nullable=False)

    employee = db.relationship("Employee", back_populates="attendance_records")

    __table_args__ = (db.UniqueConstraint("employee_id", "date", name="uq_attendance_emp_date"),)

    def calculate_working_hours(self):
        start_dt = datetime.combine(self.date, self.start_time)
        finish_dt = datetime.combine(self.date, self.finish_time)
        delta = (finish_dt - start_dt).total_seconds() / 60.0 - self.lunch_break
        return round(delta / 60.0, 2)

    def working_time_display(self):
        start_dt = datetime.combine(self.date, self.start_time)
        finish_dt = datetime.combine(self.date, self.finish_time)
        minutes = int((finish_dt - start_dt).total_seconds() / 60.0 - self.lunch_break)
        if minutes < 0:
            minutes = 0
        return f"{minutes // 60}h {minutes % 60:02d}m"
