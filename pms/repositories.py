from datetime import date, timedelta
from .extensions import db
from .models import (
    Employee, Department, Position, Transfer, PositionChange,
    LeaveRequest, AttendanceRecord, Company, LeaveStatus,
)


class EmployeeRepository:
    def get(self, employee_id):
        return db.session.get(Employee, employee_id)

    def get_by_username(self, username):
        return db.session.query(Employee).filter_by(username=username).first()

    def get_by_email(self, email):
        return db.session.query(Employee).filter_by(_email=email).first()

    def list_all(self):
        return db.session.query(Employee).order_by(Employee.surname).all()

    def list_by_department(self, department_id):
        return db.session.query(Employee).filter_by(department_id=department_id).order_by(Employee.surname).all()

    def search(self, name=None, department_id=None, position_id=None):
        q = db.session.query(Employee)
        if name:
            like = f"%{name.lower()}%"
            q = q.filter(db.or_(
                db.func.lower(Employee.name).like(like),
                db.func.lower(Employee.surname).like(like),
            ))
        if department_id:
            q = q.filter(Employee.department_id == department_id)
        if position_id:
            q = q.filter(Employee.position_id == position_id)
        return q.order_by(Employee.surname).all()

    def add(self, employee):
        db.session.add(employee)

    def delete(self, employee):
        db.session.delete(employee)


class DepartmentRepository:
    def get(self, department_id):
        return db.session.get(Department, department_id)

    def get_by_code(self, code):
        return db.session.query(Department).filter_by(code=code).first()

    def list_all(self):
        return db.session.query(Department).order_by(Department.name).all()

    def add(self, department):
        db.session.add(department)

    def delete(self, department):
        db.session.delete(department)


class PositionRepository:
    def get(self, position_id):
        return db.session.get(Position, position_id)

    def list_all(self):
        return db.session.query(Position).order_by(Position.title).all()

    def add(self, position):
        db.session.add(position)

    def delete(self, position):
        db.session.delete(position)


class TransferRepository:
    def add(self, transfer):
        db.session.add(transfer)

    def list_all(self):
        return db.session.query(Transfer).order_by(Transfer.date_time.desc()).all()

    def list_by_department(self, department_id):
        return db.session.query(Transfer).filter(
            db.or_(
                Transfer.source_department_id == department_id,
                Transfer.destination_department_id == department_id,
            )
        ).order_by(Transfer.date_time.desc()).all()

    def list_by_employee(self, employee_id):
        return db.session.query(Transfer).filter_by(employee_id=employee_id).order_by(Transfer.date_time.desc()).all()


class PositionChangeRepository:
    def add(self, change):
        db.session.add(change)

    def list_all(self):
        return db.session.query(PositionChange).order_by(PositionChange.date_time.desc()).all()

    def list_by_department(self, department_id):
        return db.session.query(PositionChange).join(Employee, PositionChange.employee_id == Employee.id).filter(
            Employee.department_id == department_id
        ).order_by(PositionChange.date_time.desc()).all()

    def list_by_employee(self, employee_id):
        return db.session.query(PositionChange).filter_by(employee_id=employee_id).order_by(PositionChange.date_time.desc()).all()


class LeaveRepository:
    def get(self, request_id):
        return db.session.get(LeaveRequest, request_id)

    def add(self, leave_request):
        db.session.add(leave_request)

    def list_by_employee(self, employee_id):
        return db.session.query(LeaveRequest).filter_by(employee_id=employee_id).order_by(LeaveRequest.date_of_request.desc()).all()

    def list_by_supervisor(self, supervisor_id):
        return db.session.query(LeaveRequest).filter_by(supervisor_id=supervisor_id).order_by(LeaveRequest.date_of_request.desc()).all()

    def list_all(self):
        return db.session.query(LeaveRequest).order_by(LeaveRequest.date_of_request.desc()).all()

    def count_for_week(self, employee_id, any_date):
        start_of_week = any_date - timedelta(days=any_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        return db.session.query(LeaveRequest).filter(
            LeaveRequest.employee_id == employee_id,
            LeaveRequest.date_of_request >= start_of_week,
            LeaveRequest.date_of_request <= end_of_week,
        ).count()


class AttendanceRepository:
    def get(self, record_id):
        return db.session.get(AttendanceRecord, record_id)

    def add(self, record):
        db.session.add(record)

    def find_by_employee_and_date(self, employee_id, on_date):
        return db.session.query(AttendanceRecord).filter_by(employee_id=employee_id, date=on_date).first()

    def list_by_employee(self, employee_id):
        return db.session.query(AttendanceRecord).filter_by(employee_id=employee_id).order_by(AttendanceRecord.date.desc()).all()

    def list_by_department(self, department_id):
        return db.session.query(AttendanceRecord).join(Employee).filter(
            Employee.department_id == department_id
        ).order_by(AttendanceRecord.date.desc()).all()


class CompanyRepository:
    def get_main(self):
        return db.session.query(Company).first()
