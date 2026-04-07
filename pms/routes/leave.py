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


def parse_date(value, field_name):
    if not value:
        raise ServiceError(f"{field_name} is required")
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise ServiceError(f"{field_name} has invalid format")


@bp.route("/")
@login_required
def my_requests():
    requests_list = LeaveRepository().list_by_employee(current_user.id)
    return render_template("leave/list.html", requests=requests_list, leave_types=LeaveType)


@bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    form = {"type": "VACATION", "start_date": "", "end_date": "", "reason": ""}
    if request.method == "POST":
        form = {
            "type": request.form.get("type", "VACATION"),
            "start_date": request.form.get("start_date", ""),
            "end_date": request.form.get("end_date", ""),
            "reason": request.form.get("reason", "").strip(),
        }
        try:
            LeaveService().submit(
                employee=current_user,
                type_str=form["type"],
                start_date=parse_date(form["start_date"], "Start date"),
                end_date=parse_date(form["end_date"], "End date"),
                reason=form["reason"],
            )
            flash("Leave request submitted", "ok")
            return redirect(url_for("leave.my_requests"))
        except ServiceError as e:
            flash(str(e), "error")
    return render_template("leave/new.html", leave_types=LeaveType, form=form)


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
