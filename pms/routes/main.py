import calendar
from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..repositories import (
    EmployeeRepository, TransferRepository, PositionChangeRepository,
    LeaveRepository, AttendanceRepository,
)
from ..models import LeaveStatus
from ..services import EmployeeService, ServiceError

bp = Blueprint("main", __name__)


@bp.route("/")
@login_required
def dashboard():
    return render_template("dashboard.html")


@bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        try:
            current_user.update_contact_details(
                request.form.get("email", "").strip(),
                request.form.get("phone", "").strip(),
            )
            from ..extensions import db
            db.session.commit()
            flash("Contact details updated", "ok")
        except (ValueError, ServiceError) as e:
            flash(str(e), "error")
        return redirect(url_for("main.profile"))
    return render_template("profile.html")


@bp.route("/history")
@login_required
def history():
    transfers = TransferRepository().list_by_employee(current_user.id)
    changes = PositionChangeRepository().list_by_employee(current_user.id)
    return render_template("history.html", transfers=transfers, changes=changes)


@bp.route("/calendar")
@login_required
def personal_calendar():
    today = date.today()
    year = request.args.get("year", type=int) or today.year
    month = request.args.get("month", type=int) or today.month

    leaves = [r for r in LeaveRepository().list_by_employee(current_user.id)
              if r.status == LeaveStatus.APPROVED]
    attendance = AttendanceRepository().list_by_employee(current_user.id)

    leave_days = {}
    for r in leaves:
        d = r.start_date
        while d <= r.end_date:
            if d.year == year and d.month == month:
                leave_days[d.day] = r.type.value
            d = date.fromordinal(d.toordinal() + 1)

    attendance_days = {a.date.day: a for a in attendance
                       if a.date.year == year and a.date.month == month}

    cal = calendar.Calendar(firstweekday=0)
    weeks = cal.monthdayscalendar(year, month)

    prev_month = (month - 1) or 12
    prev_year = year - 1 if month == 1 else year
    next_month = (month % 12) + 1
    next_year = year + 1 if month == 12 else year

    return render_template("calendar.html",
                           year=year, month=month,
                           month_name=calendar.month_name[month],
                           weeks=weeks,
                           leave_days=leave_days,
                           attendance_days=attendance_days,
                           prev_year=prev_year, prev_month=prev_month,
                           next_year=next_year, next_month=next_month)
