import os
import tempfile
import pytest


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.environ["PMS_DB_PATH"] = db_path
    os.environ["PMS_SEED"] = "full"

    from pms import create_app
    from pms.extensions import db
    from pms.seed import seed_if_empty

    app = create_app()
    app.config["TESTING"] = True
    with app.app_context():
        db.drop_all()
        db.create_all()
        seed_if_empty()

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


def login(client, username, password):
    return client.post("/login", data={"username": username, "password": password},
                       follow_redirects=True)


@pytest.fixture
def admin_client(client):
    login(client, "adminPMS", "Ip-2026!")
    return client


@pytest.fixture
def manager_client(client):
    login(client, "mgr_eng", "manager1")
    return client


@pytest.fixture
def employee_client(client):
    login(client, "employee1", "employee1")
    return client
