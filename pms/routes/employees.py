from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from ..models import Administrator, Manager
from ..repositories import EmployeeRepository, DepartmentRepository, PositionRepository
from ..services import EmployeeService, ServiceError
from ._helpers import parse_optional_date, parse_int

bp = Blueprint("employees", __name__, url_prefix="/employees")


def admin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not isinstance(current_user, Administrator):
            abort(403)
        return view(*args, **kwargs)
    return wrapper


def manager_or_admin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not isinstance(current_user, Manager):
            abort(403)
        return view(*args, **kwargs)
    return wrapper


def _form_from_request():
    return {
        "username": request.form.get("username", "").strip(),
        "password": request.form.get("password", ""),
        "name": request.form.get("name", "").strip(),
        "surname": request.form.get("surname", "").strip(),
        "email": request.form.get("email", "").strip(),
        "phone": request.form.get("phone", "").strip(),
        "dob": request.form.get("dob", ""),
        "department_id": request.form.get("department_id", ""),
        "position_id": request.form.get("position_id", ""),
        "role": request.form.get("role", "employee"),
    }


@bp.route("/")
@login_required
@manager_or_admin_required
def list_employees():
    name = request.args.get("name", "").strip()
    dept = request.args.get("department_id", type=int)
    pos = request.args.get("position_id", type=int)
    repo = EmployeeRepository()
    if isinstance(current_user, Administrator):
        employees = repo.search(name=name, department_id=dept, position_id=pos)
    else:
        employees = repo.search(name=name, department_id=current_user.department_id, position_id=pos)
    departments = DepartmentRepository().list_all()
    positions = PositionRepository().list_all()
    return render_template("employees/list.html", employees=employees,
                           departments=departments, positions=positions,
                           filter_name=name, filter_dept=dept, filter_pos=pos)


@bp.route("/<int:employee_id>")
@login_required
@manager_or_admin_required
def detail(employee_id):
    emp = EmployeeRepository().get(employee_id)
    if emp is None or not current_user.can_view_employee(emp):
        abort(404)
    return render_template("employees/detail.html", emp=emp)


@bp.route("/new", methods=["GET", "POST"])
@login_required
@admin_required
def new():
    departments = DepartmentRepository().list_all()
    positions = PositionRepository().list_all()
    form = {"username": "", "password": "", "name": "", "surname": "",
            "email": "", "phone": "", "dob": "", "department_id": "",
            "position_id": "", "role": "employee"}
    if request.method == "POST":
        form = _form_from_request()
        try:
            EmployeeService().create_employee(
                role=form["role"],
                username=form["username"],
                password=form["password"],
                name=form["name"],
                surname=form["surname"],
                email=form["email"],
                phone=form["phone"],
                dob=parse_optional_date(form["dob"], "Date of birth"),
                department_id=parse_int(form["department_id"], "Department"),
                position_id=parse_int(form["position_id"], "Position"),
            )
            flash("Employee created", "ok")
            return redirect(url_for("employees.list_employees"))
        except ServiceError as e:
            flash(str(e), "error")
        except ValueError as e:
            flash(str(e), "error")
    return render_template("employees/form.html", emp=None, form=form,
                           departments=departments, positions=positions)


@bp.route("/<int:employee_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit(employee_id):
    emp = EmployeeRepository().get(employee_id)
    if emp is None:
        abort(404)
    departments = DepartmentRepository().list_all()
    positions = PositionRepository().list_all()
    form = {
        "name": emp.name,
        "surname": emp.surname,
        "email": emp.email,
        "phone": emp.phone_number or "",
        "dob": emp.date_of_birth.isoformat() if emp.date_of_birth else "",
        "department_id": str(emp.department_id) if emp.department_id else "",
        "position_id": str(emp.position_id) if emp.position_id else "",
        "role": emp.role,
    }
    if request.method == "POST":
        form = _form_from_request()
        try:
            EmployeeService().edit_employee(
                employee_id=emp.id,
                name=form["name"],
                surname=form["surname"],
                email=form["email"],
                phone=form["phone"],
                dob=parse_optional_date(form["dob"], "Date of birth"),
                department_id=parse_int(form["department_id"], "Department"),
                position_id=parse_int(form["position_id"], "Position"),
                role=form["role"],
            )
            flash("Employee updated", "ok")
            return redirect(url_for("employees.list_employees"))
        except ServiceError as e:
            flash(str(e), "error")
        except ValueError as e:
            flash(str(e), "error")
    return render_template("employees/form.html", emp=emp, form=form,
                           departments=departments, positions=positions)


@bp.route("/<int:employee_id>/reset-password", methods=["GET", "POST"])
@login_required
@admin_required
def reset_password(employee_id):
    emp = EmployeeRepository().get(employee_id)
    if emp is None:
        abort(404)
    if request.method == "POST":
        new_pw = request.form.get("password", "").strip()
        confirm = request.form.get("confirm", "").strip()
        if not new_pw:
            flash("Password cannot be empty.", "error")
        elif new_pw != confirm:
            flash("Passwords do not match.", "error")
        elif len(new_pw) < 6:
            flash("Password must be at least 6 characters.", "error")
        else:
            emp.set_password(new_pw)
            from ..extensions import db
            db.session.commit()
            flash(f"Password for {emp.full_name} has been reset.", "ok")
            return redirect(url_for("employees.detail", employee_id=emp.id))
    return render_template("employees/reset_password.html", emp=emp)


@bp.route("/<int:employee_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete(employee_id):
    try:
        EmployeeService().delete_employee(employee_id)
        flash("Employee deleted", "ok")
    except ServiceError as e:
        flash(str(e), "error")
    return redirect(url_for("employees.list_employees"))
