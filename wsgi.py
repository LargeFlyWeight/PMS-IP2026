"""WSGI entry point for production hosting (e.g. PythonAnywhere).

Set the following environment variables before importing:
    PMS_SECRET_KEY  — long random string
    PMS_DB_PATH     — absolute path to the SQLite file (writable, persistent)
    PMS_SEED        — "minimal" (only admin) or "full" (admin + sample users)
"""

from pms import create_app
from pms.extensions import db
from pms.seed import seed_if_empty

application = create_app()

with application.app_context():
    db.create_all()
    seed_if_empty()
