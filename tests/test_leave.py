from datetime import date, timedelta


def _date(offset):
    return (date.today() + timedelta(days=offset)).isoformat()


def test_employee_submits_leave_pending(employee_client):
    r = employee_client.post("/leave/new", data={
        "type": "VACATION",
        "start_date": _date(7),
        "end_date": _date(10),
        "reason": "Family trip",
    }, follow_redirects=True)
    assert b"Pending" in r.data


def test_admin_leave_auto_approved(admin_client):
    r = admin_client.post("/leave/new", data={
        "type": "PERSONAL_LEAVE",
        "start_date": _date(1),
        "end_date": _date(2),
        "reason": "Errand",
    }, follow_redirects=True)
    assert b"Approved" in r.data


def test_invalid_dates_rejected(employee_client):
    r = employee_client.post("/leave/new", data={
        "type": "VACATION",
        "start_date": _date(10),
        "end_date": _date(5),
        "reason": "Bad dates",
    }, follow_redirects=True)
    assert b"Start date must be before end date" in r.data


def test_weekly_limit_two(employee_client):
    for i, ok in enumerate([True, True, False]):
        r = employee_client.post("/leave/new", data={
            "type": "SICK_LEAVE",
            "start_date": _date(20 + i),
            "end_date": _date(21 + i),
            "reason": f"req{i}",
        }, follow_redirects=True)
        if not ok:
            assert b"at most 2 leave requests per week" in r.data


def test_manager_approves_employee_leave(employee_client, client):
    employee_client.post("/leave/new", data={
        "type": "VACATION",
        "start_date": _date(30),
        "end_date": _date(31),
        "reason": "trip",
    }, follow_redirects=True)
    client.get("/logout")
    client.post("/login", data={"username": "mgr_eng", "password": "manager1"})
    r = client.get("/leave/department")
    assert b"trip" in r.data
    r = client.post("/leave/1/approve", follow_redirects=True)
    assert b"Approved" in r.data


def test_manager_rejects_leave(employee_client, client):
    employee_client.post("/leave/new", data={
        "type": "VACATION",
        "start_date": _date(40),
        "end_date": _date(41),
        "reason": "no",
    }, follow_redirects=True)
    client.get("/logout")
    client.post("/login", data={"username": "mgr_eng", "password": "manager1"})
    r = client.post("/leave/1/reject", follow_redirects=True)
    assert b"Rejected" in r.data
