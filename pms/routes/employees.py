from datetime import datetime
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from ..models import Administrator, Manager
from ..repositories import EmployeeRepository, DepartmentRepository, PositionRepository
from ..services import EmployeeService, ServiceError

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


def parse_date(value):
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


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
    if request.method == "POST":
        try:
            EmployeeService().create_employee(
                role=request.form.get("role", "employee"),
                username=request.form.get("username", "").strip(),
                password=request.form.get("password", ""),
                name=request.form.get("name", "").strip(),
                surname=request.form.get("surname", "").strip(),
                email=request.form.get("email", "").strip(),
                phone=request.form.get("phone", "").strip(),
                dob=parse_date(request.form.get("dob")),
                department_id=int(request.form.get("department_id")),
                position_id=int(request.form.get("position_id")),
            )
            flash("Employee created", "ok")
            return redirect(url_for("employees.list_employees"))
        except (ServiceError, ValueError) as e:
            flash(str(e), "error")
    return render_template("employees/form.html", emp=None,
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
    if request.method == "POST":
        try:
            EmployeeService().edit_employee(
                employee_id=emp.id,
                name=request.form.get("name", "").strip(),
                surname=request.form.get("surname", "").strip(),
                email=request.form.get("email", "").strip(),
                phone=request.form.get("phone", "").strip(),
                dob=parse_date(request.form.get("dob")),
                department_id=int(request.form.get("department_id")),
                position_id=int(request.form.get("position_id")),
                role=request.form.get("role"),
            )
            flash("Employee updated", "ok")
            return redirect(url_for("employees.list_employees"))
        except (ServiceError, ValueError) as e:
            flash(str(e), "error")
    return render_template("employees/form.html", emp=emp,
                           departments=departments, positions=positions)


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
