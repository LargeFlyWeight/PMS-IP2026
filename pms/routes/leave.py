from datetime import datetime
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from ..models import Administrator, Manager, LeaveType
from ..repositories import LeaveRepository
from ..services import LeaveService, ServiceError

bp = Blueprint("leave", __name__, url_prefix="/leave")


def manager_or_admin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not isinstance(current_user, Manager):
            abort(403)
        return view(*args, **kwargs)
    return wrapper


def parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date()


@bp.route("/")
@login_required
def my_requests():
    requests_list = LeaveRepository().list_by_employee(current_user.id)
    return render_template("leave/list.html", requests=requests_list, leave_types=LeaveType)


@bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    if request.method == "POST":
        try:
            LeaveService().submit(
                employee=current_user,
                type_str=request.form.get("type"),
                start_date=parse_date(request.form.get("start_date")),
                end_date=parse_date(request.form.get("end_date")),
                reason=request.form.get("reason", "").strip(),
            )
            flash("Leave request submitted", "ok")
            return redirect(url_for("leave.my_requests"))
        except (ServiceError, ValueError) as e:
            flash(str(e), "error")
    return render_template("leave/new.html", leave_types=LeaveType)


@bp.route("/department")
@login_required
@manager_or_admin_required
def department_requests():
    repo = LeaveRepository()
    if isinstance(current_user, Administrator):
        requests_list = repo.list_all()
    else:
        requests_list = repo.list_by_supervisor(current_user.id)
    return render_template("leave/department.html", requests=requests_list)


@bp.route("/<int:request_id>/approve", methods=["POST"])
@login_required
@manager_or_admin_required
def approve(request_id):
    try:
        LeaveService().approve(request_id, current_user)
        flash("Request approved", "ok")
    except ServiceError as e:
        flash(str(e), "error")
    return redirect(url_for("leave.department_requests"))


@bp.route("/<int:request_id>/reject", methods=["POST"])
@login_required
@manager_or_admin_required
def reject(request_id):
    try:
        LeaveService().reject(request_id, current_user)
        flash("Request rejected", "ok")
    except ServiceError as e:
        flash(str(e), "error")
    return redirect(url_for("leave.department_requests"))
