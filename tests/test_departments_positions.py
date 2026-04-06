def test_admin_lists_departments(admin_client):
    r = admin_client.get("/departments/")
    assert b"Engineering" in r.data


def test_manager_cannot_access_departments(manager_client):
    assert manager_client.get("/departments/").status_code == 403


def test_create_department(admin_client):
    r = admin_client.post("/departments/new", data={
        "code": "QA", "name": "Quality Assurance", "location": "777",
    }, follow_redirects=True)
    assert b"Quality Assurance" in r.data


def test_duplicate_department_code_rejected(admin_client):
    r = admin_client.post("/departments/new", data={
        "code": "ENG", "name": "Other", "location": "1",
    }, follow_redirects=True)
    assert b"already exists" in r.data


def test_cannot_delete_department_with_employees(admin_client):
    r = admin_client.post("/departments/2/delete", follow_redirects=True)
    assert b"still has employees" in r.data


def test_create_position(admin_client):
    r = admin_client.post("/positions/new", data={
        "title": "QA Engineer", "salary_grade": "B3", "description": "Tests stuff",
    }, follow_redirects=True)
    assert b"QA Engineer" in r.data


def test_cannot_delete_position_in_use(admin_client):
    r = admin_client.post("/positions/3/delete", follow_redirects=True)
    assert b"currently held" in r.data
