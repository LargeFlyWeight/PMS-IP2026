from datetime import date
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from ..models import Administrator, Manager
from ..repositories import AttendanceRepository
from ..services import AttendanceService, ServiceError
from ._helpers import parse_date, parse_time, parse_int

bp = Blueprint("attendance", __name__, url_prefix="/attendance")


def manager_or_admin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not isinstance(current_user, Manager):
            abort(403)
        return view(*args, **kwargs)
    return wrapper


@bp.route("/")
@login_required
def my_attendance():
    records = AttendanceRepository().list_by_employee(current_user.id)
    return render_template("attendance/list.html", records=records)


@bp.route("/new", methods=["GET", "POST"])
@login_required
def record():
    form = {"date": date.today().isoformat(), "start_time": "",
            "lunch_break": "0", "finish_time": ""}
    if request.method == "POST":
        form = {
            "date": request.form.get("date", ""),
            "start_time": request.form.get("start_time", ""),
            "lunch_break": request.form.get("lunch_break", "0"),
            "finish_time": request.form.get("finish_time", ""),
        }
        try:
            AttendanceService().record(
                employee=current_user,
                on_date=parse_date(form["date"], "Date"),
                start_time=parse_time(form["start_time"], "Start time"),
                lunch_break=parse_int(form["lunch_break"], "Lunch break"),
                finish_time=parse_time(form["finish_time"], "Finish time"),
            )
            flash("Attendance recorded", "ok")
            return redirect(url_for("attendance.my_attendance"))
        except ServiceError as e:
            flash(str(e), "error")
    return render_template("attendance/record.html", form=form)


@bp.route("/department")
@login_required
@manager_or_admin_required
def department_attendance():
    if isinstance(current_user, Administrator) and request.args.get("all"):
        from ..models import AttendanceRecord
        from ..extensions import db
        records = db.session.query(AttendanceRecord).order_by(AttendanceRecord.date.desc()).all()
    else:
        records = AttendanceRepository().list_by_department(current_user.department_id)
    return render_template("attendance/department.html", records=records)


@bp.route("/<int:record_id>/edit", methods=["GET", "POST"])
@login_required
@manager_or_admin_required
def edit(record_id):
    record = AttendanceRepository().get(record_id)
    if record is None:
        abort(404)
    if not isinstance(current_user, Administrator) and record.employee.department_id != current_user.department_id:
        abort(403)
    form = {
        "start_time": record.start_time.strftime("%H:%M"),
        "lunch_break": str(record.lunch_break),
        "finish_time": record.finish_time.strftime("%H:%M"),
    }
    if request.method == "POST":
        form = {
            "start_time": request.form.get("start_time", ""),
            "lunch_break": request.form.get("lunch_break", "0"),
            "finish_time": request.form.get("finish_time", ""),
        }
        try:
            AttendanceService().edit(
                record_id=record.id,
                start_time=parse_time(form["start_time"], "Start time"),
                lunch_break=parse_int(form["lunch_break"], "Lunch break"),
                finish_time=parse_time(form["finish_time"], "Finish time"),
            )
            flash("Attendance updated", "ok")
            return redirect(url_for("attendance.department_attendance"))
        except ServiceError as e:
            flash(str(e), "error")
    return render_template("attendance/edit.html", record=record, form=form)
