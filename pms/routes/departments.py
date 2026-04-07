from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from ..models import Administrator
from ..repositories import DepartmentRepository, EmployeeRepository, CompanyRepository
from ..services import DepartmentService, ServiceError
from ._helpers import parse_int

bp = Blueprint("departments", __name__, url_prefix="/departments")


def admin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not isinstance(current_user, Administrator):
            abort(403)
        return view(*args, **kwargs)
    return wrapper


@bp.route("/")
@login_required
@admin_required
def list_departments():
    departments = DepartmentRepository().list_all()
    return render_template("departments/list.html", departments=departments)


@bp.route("/new", methods=["GET", "POST"])
@login_required
@admin_required
def new():
    form = {"code": "", "name": "", "location": ""}
    if request.method == "POST":
        form = {
            "code": request.form.get("code", "").strip(),
            "name": request.form.get("name", "").strip(),
            "location": request.form.get("location", "").strip(),
        }
        try:
            company = CompanyRepository().get_main()
            DepartmentService().create_department(
                code=form["code"],
                name=form["name"],
                location=form["location"],
                company_id=company.id,
            )
            flash("Department created", "ok")
            return redirect(url_for("departments.list_departments"))
        except ServiceError as e:
            flash(str(e), "error")
    return render_template("departments/form.html", dept=None, form=form)


@bp.route("/<int:department_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit(department_id):
    dept = DepartmentRepository().get(department_id)
    if dept is None:
        abort(404)
    form = {"code": dept.code, "name": dept.name, "location": dept.location or ""}
    if request.method == "POST":
        form = {
            "code": dept.code,
            "name": request.form.get("name", "").strip(),
            "location": request.form.get("location", "").strip(),
        }
        try:
            DepartmentService().edit_department(
                department_id=dept.id,
                name=form["name"],
                location=form["location"],
            )
            flash("Department updated", "ok")
            return redirect(url_for("departments.list_departments"))
        except ServiceError as e:
            flash(str(e), "error")
    return render_template("departments/form.html", dept=dept, form=form)


@bp.route("/<int:department_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete(department_id):
    try:
        DepartmentService().delete_department(department_id)
        flash("Department deleted", "ok")
    except ServiceError as e:
        flash(str(e), "error")
    return redirect(url_for("departments.list_departments"))


@bp.route("/<int:department_id>/assign-manager", methods=["GET", "POST"])
@login_required
@admin_required
def assign_manager(department_id):
    dept = DepartmentRepository().get(department_id)
    if dept is None:
        abort(404)
    employees = EmployeeRepository().list_by_department(dept.id)
    form = {"employee_id": ""}
    if request.method == "POST":
        form = {"employee_id": request.form.get("employee_id", "")}
        try:
            DepartmentService().assign_manager(
                dept.id, parse_int(form["employee_id"], "Employee")
            )
            flash("Manager assigned", "ok")
            return redirect(url_for("departments.list_departments"))
        except ServiceError as e:
            flash(str(e), "error")
    return render_template("departments/assign_manager.html", dept=dept,
                           employees=employees, form=form)
