from datetime import date


def test_record_attendance(employee_client):
    r = employee_client.post("/attendance/new", data={
        "date": date.today().isoformat(),
        "start_time": "09:00",
        "lunch_break": "30",
        "finish_time": "17:00",
    }, follow_redirects=True)
    assert r.status_code == 200
    r = employee_client.get("/attendance/")
    assert b"09:00" in r.data


def test_attendance_lunch_out_of_range(employee_client):
    r = employee_client.post("/attendance/new", data={
        "date": date.today().isoformat(),
        "start_time": "09:00",
        "lunch_break": "120",
        "finish_time": "17:00",
    }, follow_redirects=True)
    assert b"Lunch break must be between 0 and 60" in r.data


def test_attendance_exceeds_8_hours(employee_client):
    r = employee_client.post("/attendance/new", data={
        "date": date.today().isoformat(),
        "start_time": "08:00",
        "lunch_break": "0",
        "finish_time": "20:00",
    }, follow_redirects=True)
    assert b"exceeds 8 hours" in r.data


def test_attendance_one_per_day(employee_client):
    today = date.today().isoformat()
    employee_client.post("/attendance/new", data={
        "date": today, "start_time": "09:00", "lunch_break": "0", "finish_time": "17:00",
    }, follow_redirects=True)
    r = employee_client.post("/attendance/new", data={
        "date": today, "start_time": "10:00", "lunch_break": "0", "finish_time": "17:00",
    }, follow_redirects=True)
    assert b"already exists" in r.data


def test_update_own_contact_details(employee_client):
    r = employee_client.post("/profile", data={
        "email": "peteris.new@tsi.lv", "phone": "+371 11111111",
    }, follow_redirects=True)
    assert b"updated" in r.data
    assert b"peteris.new@tsi.lv" in r.data


def test_invalid_email_rejected(employee_client):
    r = employee_client.post("/profile", data={
        "email": "not-an-email", "phone": "",
    }, follow_redirects=True)
    assert b"Invalid email" in r.data


def test_view_own_history_accessible(employee_client):
    assert employee_client.get("/history").status_code == 200
