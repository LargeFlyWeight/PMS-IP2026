from datetime import datetime, date, time
from .extensions import db
from .models import (
    Employee, Manager, Administrator, Department, Position,
    Transfer, PositionChange, LeaveRequest, AttendanceRecord,
    LeaveType, LeaveStatus,
)
from .repositories import (
    EmployeeRepository, DepartmentRepository, PositionRepository,
    TransferRepository, PositionChangeRepository, LeaveRepository,
    AttendanceRepository,
)


class ServiceError(Exception):
    pass


class AuthService:
    def __init__(self):
        self.employees = EmployeeRepository()

    def authenticate(self, username, password):
        user = self.employees.get_by_username(username)
        if user is None or not user.check_password(password):
            raise ServiceError("Invalid username or password")
        return user


class EmployeeService:
    def __init__(self):
        self.employees = EmployeeRepository()
        self.departments = DepartmentRepository()
        self.positions = PositionRepository()

    def create_employee(self, role, username, password, name, surname, email,
                        phone, dob, department_id, position_id):
        if not username or not password or not name or not surname or not email:
            raise ServiceError("All required fields must be filled")
        if self.employees.get_by_username(username):
            raise ServiceError("Username already taken")
        if self.employees.get_by_email(email):
            raise ServiceError("Email already in use")
        if not self.departments.get(department_id):
            raise ServiceError("Department does not exist")
        if not self.positions.get(position_id):
            raise ServiceError("Position does not exist")

        cls = {"employee": Employee, "manager": Manager, "administrator": Administrator}.get(role, Employee)
        emp = cls(
            username=username,
            name=name,
            surname=surname,
            date_of_birth=dob,
            department_id=department_id,
            position_id=position_id,
        )
        emp.email = email
        emp.phone_number = phone
        emp.set_password(password)
        self.employees.add(emp)
        db.session.commit()
        return emp

    def edit_employee(self, employee_id, name, surname, email, phone, dob,
                      department_id, position_id, role=None):
        emp = self.employees.get(employee_id)
        if emp is None:
            raise ServiceError("Employee not found")
        emp.name = name
        emp.surname = surname
        emp.email = email
        emp.phone_number = phone
        emp.date_of_birth = dob
        emp.department_id = department_id
        emp.position_id = position_id
        if role and role != emp.role:
            emp.role = role
        db.session.commit()
        return emp

    def delete_employee(self, employee_id):
        emp = self.employees.get(employee_id)
        if emp is None:
            raise ServiceError("Employee not found")
        managed = db.session.query(Department).filter_by(manager_id=emp.id).first()
        if managed is not None:
            raise ServiceError("Employee manages a department. Reassign manager first.")
        self.employees.delete(emp)
        db.session.commit()


class DepartmentService:
    def __init__(self):
        self.departments = DepartmentRepository()
        self.employees = EmployeeRepository()

    def create_department(self, code, name, location, company_id):
        if not code or not name:
            raise ServiceError("Code and name are required")
        if self.departments.get_by_code(code):
            raise ServiceError("Department code already exists")
        dept = Department(code=code, name=name, location=location, company_id=company_id)
        self.departments.add(dept)
        db.session.commit()
        return dept

    def edit_department(self, department_id, name, location):
        dept = self.departments.get(department_id)
        if dept is None:
            raise ServiceError("Department not found")
        dept.name = name
        dept.location = location
        db.session.commit()

    def delete_department(self, department_id):
        dept = self.departments.get(department_id)
        if dept is None:
            raise ServiceError("Department not found")
        if dept.employees:
            raise ServiceError("Department still has employees")
        self.departments.delete(dept)
        db.session.commit()

    def assign_manager(self, department_id, employee_id):
        dept = self.departments.get(department_id)
        emp = self.employees.get(employee_id)
        if dept is None or emp is None:
            raise ServiceError("Department or employee not found")
        if emp.department_id != dept.id:
            raise ServiceError("Employee does not belong to this department")
        already = db.session.query(Department).filter(
            Department.manager_id == emp.id, Department.id != dept.id
        ).first()
        if already is not None:
            raise ServiceError("Employee already manages another department")
        # promote employee to manager role if currently plain
        if emp.role == "employee":
            emp.role = "manager"
        dept.manager_id = emp.id
        db.session.commit()


class PositionService:
    def __init__(self):
        self.positions = PositionRepository()

    def create_position(self, title, salary_grade, description):
        if not title or not salary_grade:
            raise ServiceError("Title and salary grade are required")
        pos = Position(title=title, salary_grade=salary_grade, description=description)
        self.positions.add(pos)
        db.session.commit()
        return pos

    def edit_position(self, position_id, title, salary_grade, description):
        pos = self.positions.get(position_id)
        if pos is None:
            raise ServiceError("Position not found")
        pos.title = title
        pos.salary_grade = salary_grade
        pos.description = description
        db.session.commit()

    def delete_position(self, position_id):
        pos = self.positions.get(position_id)
        if pos is None:
            raise ServiceError("Position not found")
        if pos.employees:
            raise ServiceError("Position is currently held by employees")
        self.positions.delete(pos)
        db.session.commit()


class TransferService:
    def __init__(self):
        self.transfers = TransferRepository()
        self.employees = EmployeeRepository()
        self.departments = DepartmentRepository()

    def transfer_employee(self, employee_id, destination_department_id):
        emp = self.employees.get(employee_id)
        dest = self.departments.get(destination_department_id)
        if emp is None or dest is None:
            raise ServiceError("Employee or department not found")
        if emp.department_id == dest.id:
            raise ServiceError("Employee already belongs to this department")
        source_id = emp.department_id
        record = Transfer(
            employee_id=emp.id,
            source_department_id=source_id,
            destination_department_id=dest.id,
        )
        self.transfers.add(record)
        emp.department_id = dest.id
        db.session.commit()
        return record


class PositionChangeService:
    def __init__(self):
        self.changes = PositionChangeRepository()
        self.employees = EmployeeRepository()
        self.positions = PositionRepository()

    def change_position(self, employee_id, new_position_id, reason):
        emp = self.employees.get(employee_id)
        new_pos = self.positions.get(new_position_id)
        if emp is None or new_pos is None:
            raise ServiceError("Employee or position not found")
        if emp.position_id == new_pos.id:
            raise ServiceError("Employee already holds this position")
        if not reason:
            raise ServiceError("Reason is required")
        change = PositionChange(
            employee_id=emp.id,
            previous_position_id=emp.position_id,
            new_position_id=new_pos.id,
            reason=reason,
        )
        self.changes.add(change)
        emp.position_id = new_pos.id
        db.session.commit()
        return change


class LeaveService:
    def __init__(self):
        self.leaves = LeaveRepository()

    def submit(self, employee, type_str, start_date, end_date, reason):
        if not reason:
            raise ServiceError("Reason is required")
        try:
            leave_type = LeaveType[type_str]
        except KeyError:
            raise ServiceError("Invalid leave type")
        if start_date > end_date:
            raise ServiceError("Start date must be before end date")
        if self.leaves.count_for_week(employee.id, date.today()) >= 2:
            raise ServiceError("You may submit at most 2 leave requests per week")

        supervisor = employee.supervisor()
        request = LeaveRequest(
            employee_id=employee.id,
            type=leave_type,
            start_date=start_date,
            end_date=end_date,
            date_of_request=date.today(),
            reason=reason,
            status=LeaveStatus.APPROVED if employee.auto_approve_leave() else LeaveStatus.PENDING,
            supervisor_id=supervisor.id if supervisor else None,
        )
        self.leaves.add(request)
        db.session.commit()
        return request

    def approve(self, request_id, current_user):
        req = self.leaves.get(request_id)
        if req is None:
            raise ServiceError("Request not found")
        if req.supervisor_id != current_user.id and not isinstance(current_user, Administrator):
            raise ServiceError("You cannot approve this request")
        req.approve()
        db.session.commit()

    def reject(self, request_id, current_user):
        req = self.leaves.get(request_id)
        if req is None:
            raise ServiceError("Request not found")
        if req.supervisor_id != current_user.id and not isinstance(current_user, Administrator):
            raise ServiceError("You cannot reject this request")
        req.reject()
        db.session.commit()


class AttendanceService:
    def __init__(self):
        self.attendance = AttendanceRepository()

    def _validate(self, lunch_break, start_time, finish_time):
        if lunch_break < 0 or lunch_break > 60:
            raise ServiceError("Lunch break must be between 0 and 60 minutes")
        if finish_time <= start_time:
            raise ServiceError("Finish time must be after start time")
        worked = (datetime.combine(date.today(), finish_time)
                  - datetime.combine(date.today(), start_time)).total_seconds() / 60.0 - lunch_break
        if worked / 60.0 > 8:
            raise ServiceError("Total working time exceeds 8 hours")

    def record(self, employee, on_date, start_time, lunch_break, finish_time):
        if self.attendance.find_by_employee_and_date(employee.id, on_date) is not None:
            raise ServiceError("Attendance for this date already exists")
        self._validate(lunch_break, start_time, finish_time)
        record = AttendanceRecord(
            employee_id=employee.id,
            date=on_date,
            start_time=start_time,
            lunch_break=lunch_break,
            finish_time=finish_time,
        )
        self.attendance.add(record)
        db.session.commit()
        return record

    def edit(self, record_id, start_time, lunch_break, finish_time):
        record = self.attendance.get(record_id)
        if record is None:
            raise ServiceError("Record not found")
        self._validate(lunch_break, start_time, finish_time)
        record.start_time = start_time
        record.lunch_break = lunch_break
        record.finish_time = finish_time
        db.session.commit()
