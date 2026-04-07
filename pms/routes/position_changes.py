from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from ..models import Administrator, Manager
from ..repositories import PositionChangeRepository, EmployeeRepository, PositionRepository, DepartmentRepository
from ..services import PositionChangeService, ServiceError
from ._helpers import parse_int

bp = Blueprint("position_changes", __name__, url_prefix="/position-changes")


def manager_or_admin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not isinstance(current_user, Manager):
            abort(403)
        return view(*args, **kwargs)
    return wrapper


def admin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not isinstance(current_user, Administrator):
            abort(403)
        return view(*args, **kwargs)
    return wrapper


@bp.route("/")
@login_required
@manager_or_admin_required
def list_changes():
    repo = PositionChangeRepository()
    if isinstance(current_user, Administrator):
        dept_filter = request.args.get("department_id", type=int)
        if dept_filter:
            changes = repo.list_by_department(dept_filter)
        else:
            changes = repo.list_all()
    else:
        changes = repo.list_by_department(current_user.department_id)
    departments = DepartmentRepository().list_all()
    return render_template("position_changes/list.html", changes=changes, departments=departments)


@bp.route("/new", methods=["GET", "POST"])
@login_required
@admin_required
def new():
    employees = EmployeeRepository().list_all()
    positions = PositionRepository().list_all()
    form = {"employee_id": "", "new_position_id": "", "reason": ""}
    if request.method == "POST":
        form = {
            "employee_id": request.form.get("employee_id", ""),
            "new_position_id": request.form.get("new_position_id", ""),
            "reason": request.form.get("reason", "").strip(),
        }
        try:
            PositionChangeService().change_position(
                employee_id=parse_int(form["employee_id"], "Employee"),
                new_position_id=parse_int(form["new_position_id"], "New position"),
                reason=form["reason"],
            )
            flash("Position changed", "ok")
            return redirect(url_for("position_changes.list_changes"))
        except ServiceError as e:
            flash(str(e), "error")
    return render_template("position_changes/new.html", employees=employees,
                           positions=positions, form=form)
