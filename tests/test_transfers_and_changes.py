def test_transfer_employee_creates_log(admin_client):
    r = admin_client.post("/transfers/new", data={
        "employee_id": "4", "destination_department_id": "3",
    }, follow_redirects=True)
    assert r.status_code == 200
    r = admin_client.get("/transfers/")
    assert b"Peteris" in r.data
    assert b"Engineering" in r.data
    assert b"Sales" in r.data


def test_transfer_same_department_rejected(admin_client):
    r = admin_client.post("/transfers/new", data={
        "employee_id": "4", "destination_department_id": "2",
    }, follow_redirects=True)
    assert b"already belongs" in r.data


def test_manager_can_view_transfer_logs(manager_client):
    assert manager_client.get("/transfers/").status_code == 200


def test_employee_cannot_view_transfer_logs(employee_client):
    assert employee_client.get("/transfers/").status_code == 403


def test_position_change_creates_log(admin_client):
    r = admin_client.post("/position-changes/new", data={
        "employee_id": "4", "new_position_id": "2", "reason": "Promotion",
    }, follow_redirects=True)
    assert r.status_code == 200
    r = admin_client.get("/position-changes/")
    assert b"Promotion" in r.data


def test_position_change_requires_reason(admin_client):
    r = admin_client.post("/position-changes/new", data={
        "employee_id": "4", "new_position_id": "2", "reason": "",
    }, follow_redirects=True)
    assert b"Reason is required" in r.data
