from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from ..models import Administrator
from ..repositories import DepartmentRepository, EmployeeRepository, CompanyRepository
from ..services import DepartmentService, ServiceError

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
    if request.method == "POST":
        try:
            company = CompanyRepository().get_main()
            DepartmentService().create_department(
                code=request.form.get("code", "").strip(),
                name=request.form.get("name", "").strip(),
                location=request.form.get("location", "").strip(),
                company_id=company.id,
            )
            flash("Department created", "ok")
            return redirect(url_for("departments.list_departments"))
        except ServiceError as e:
            flash(str(e), "error")
    return render_template("departments/form.html", dept=None)


@bp.route("/<int:department_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit(department_id):
    dept = DepartmentRepository().get(department_id)
    if dept is None:
        abort(404)
    if request.method == "POST":
        try:
            DepartmentService().edit_department(
                department_id=dept.id,
                name=request.form.get("name", "").strip(),
                location=request.form.get("location", "").strip(),
            )
            flash("Department updated", "ok")
            return redirect(url_for("departments.list_departments"))
        except ServiceError as e:
            flash(str(e), "error")
    return render_template("departments/form.html", dept=dept)


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
    if request.method == "POST":
        try:
            DepartmentService().assign_manager(dept.id, int(request.form.get("employee_id")))
            flash("Manager assigned", "ok")
            return redirect(url_for("departments.list_departments"))
        except ServiceError as e:
            flash(str(e), "error")
    return render_template("departments/assign_manager.html", dept=dept, employees=employees)
