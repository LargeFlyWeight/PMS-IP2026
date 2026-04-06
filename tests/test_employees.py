def test_admin_can_list_employees(admin_client):
    r = admin_client.get("/employees/")
    assert r.status_code == 200
    assert b"Peteris" in r.data


def test_employee_cannot_list_employees(employee_client):
    assert employee_client.get("/employees/").status_code == 403


def test_manager_sees_only_own_department(manager_client):
    r = manager_client.get("/employees/")
    assert r.status_code == 200
    assert b"Peteris" in r.data       # Engineering
    assert b"Maris" not in r.data     # Sales


def test_admin_creates_employee(admin_client):
    r = admin_client.post("/employees/new", data={
        "username": "newemp",
        "password": "pwd12345",
        "name": "New",
        "surname": "Person",
        "email": "new@tsi.lv",
        "phone": "+371 12345678",
        "dob": "1995-01-01",
        "department_id": "2",
        "position_id": "3",
        "role": "employee",
    }, follow_redirects=True)
    assert r.status_code == 200
    assert b"New Person" in r.data


def test_create_employee_duplicate_email_rejected(admin_client):
    r = admin_client.post("/employees/new", data={
        "username": "dup",
        "password": "pwd12345",
        "name": "Dup",
        "surname": "Person",
        "email": "peteris@tsi.lv",
        "phone": "",
        "dob": "1995-01-01",
        "department_id": "2",
        "position_id": "3",
        "role": "employee",
    }, follow_redirects=True)
    assert b"Email already in use" in r.data


def test_admin_edits_employee(admin_client):
    r = admin_client.post("/employees/4/edit", data={
        "name": "Peteris",
        "surname": "Updated",
        "email": "peteris@tsi.lv",
        "phone": "+371 99999999",
        "dob": "1995-03-15",
        "department_id": "2",
        "position_id": "3",
        "role": "employee",
    }, follow_redirects=True)
    assert b"Updated" in r.data


def test_admin_deletes_employee(admin_client):
    r = admin_client.post("/employees/6/delete", follow_redirects=True)
    assert b"Maris" not in r.data


def test_cannot_delete_manager_of_department(admin_client):
    r = admin_client.post("/employees/2/delete", follow_redirects=True)
    assert b"manages a department" in r.data


def test_search_by_name(admin_client):
    r = admin_client.get("/employees/?name=peteris")
    assert b"Peteris" in r.data
    assert b"Liga" not in r.data
