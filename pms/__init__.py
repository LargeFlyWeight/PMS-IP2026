import os
from flask import Flask
from .extensions import db, login_manager


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")

    db_path = os.environ.get("PMS_DB_PATH", os.path.join(os.getcwd(), "pms.db"))
    app.config["SECRET_KEY"] = os.environ.get("PMS_SECRET_KEY", "dev-secret-change-me")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    from .models import Employee

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(Employee, int(user_id))

    from .routes.auth import bp as auth_bp
    from .routes.main import bp as main_bp
    from .routes.employees import bp as employees_bp
    from .routes.departments import bp as departments_bp
    from .routes.positions import bp as positions_bp
    from .routes.transfers import bp as transfers_bp
    from .routes.position_changes import bp as pc_bp
    from .routes.leave import bp as leave_bp
    from .routes.attendance import bp as attendance_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(employees_bp)
    app.register_blueprint(departments_bp)
    app.register_blueprint(positions_bp)
    app.register_blueprint(transfers_bp)
    app.register_blueprint(pc_bp)
    app.register_blueprint(leave_bp)
    app.register_blueprint(attendance_bp)

    return app
