from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from ..models import Administrator
from ..repositories import PositionRepository
from ..services import PositionService, ServiceError

bp = Blueprint("positions", __name__, url_prefix="/positions")


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
def list_positions():
    positions = PositionRepository().list_all()
    return render_template("positions/list.html", positions=positions)


@bp.route("/new", methods=["GET", "POST"])
@login_required
@admin_required
def new():
    if request.method == "POST":
        try:
            PositionService().create_position(
                title=request.form.get("title", "").strip(),
                salary_grade=request.form.get("salary_grade", "").strip(),
                description=request.form.get("description", "").strip(),
            )
            flash("Position created", "ok")
            return redirect(url_for("positions.list_positions"))
        except ServiceError as e:
            flash(str(e), "error")
    return render_template("positions/form.html", pos=None)


@bp.route("/<int:position_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit(position_id):
    pos = PositionRepository().get(position_id)
    if pos is None:
        abort(404)
    if request.method == "POST":
        try:
            PositionService().edit_position(
                position_id=pos.id,
                title=request.form.get("title", "").strip(),
                salary_grade=request.form.get("salary_grade", "").strip(),
                description=request.form.get("description", "").strip(),
            )
            flash("Position updated", "ok")
            return redirect(url_for("positions.list_positions"))
        except ServiceError as e:
            flash(str(e), "error")
    return render_template("positions/form.html", pos=pos)


@bp.route("/<int:position_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete(position_id):
    try:
        PositionService().delete_position(position_id)
        flash("Position deleted", "ok")
    except ServiceError as e:
        flash(str(e), "error")
    return redirect(url_for("positions.list_positions"))
