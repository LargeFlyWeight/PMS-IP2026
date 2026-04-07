from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from ..models import Administrator, Manager
from ..repositories import TransferRepository, EmployeeRepository, DepartmentRepository
from ..services import TransferService, ServiceError
from ._helpers import parse_int

bp = Blueprint("transfers", __name__, url_prefix="/transfers")


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
def list_transfers():
    repo = TransferRepository()
    if isinstance(current_user, Administrator):
        dept_filter = request.args.get("department_id", type=int)
        if dept_filter:
            transfers = repo.list_by_department(dept_filter)
        else:
            transfers = repo.list_all()
    else:
        transfers = repo.list_by_department(current_user.department_id)
    departments = DepartmentRepository().list_all()
    return render_template("transfers/list.html", transfers=transfers, departments=departments)


@bp.route("/new", methods=["GET", "POST"])
@login_required
@admin_required
def new():
    employees = EmployeeRepository().list_all()
    departments = DepartmentRepository().list_all()
    form = {"employee_id": "", "destination_department_id": ""}
    if request.method == "POST":
        form = {
            "employee_id": request.form.get("employee_id", ""),
            "destination_department_id": request.form.get("destination_department_id", ""),
        }
        try:
            TransferService().transfer_employee(
                employee_id=parse_int(form["employee_id"], "Employee"),
                destination_department_id=parse_int(form["destination_department_id"], "Destination department"),
            )
            flash("Employee transferred", "ok")
            return redirect(url_for("transfers.list_transfers"))
        except ServiceError as e:
            flash(str(e), "error")
    return render_template("transfers/new.html", employees=employees,
                           departments=departments, form=form)
