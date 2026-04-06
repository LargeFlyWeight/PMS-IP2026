def test_login_page_loads(client):
    assert client.get("/login").status_code == 200


def test_login_success_redirects_to_dashboard(client):
    r = client.post("/login", data={"username": "adminPMS", "password": "Ip-2026!"},
                    follow_redirects=True)
    assert r.status_code == 200
    assert b"Welcome" in r.data


def test_login_wrong_password(client):
    r = client.post("/login", data={"username": "adminPMS", "password": "nope"},
                    follow_redirects=True)
    assert b"Invalid" in r.data


def test_protected_route_redirects_anonymous(client):
    r = client.get("/")
    assert r.status_code == 302
    assert "/login" in r.headers["Location"]


def test_logout(admin_client):
    r = admin_client.get("/logout", follow_redirects=False)
    assert r.status_code == 302


def test_admin_sees_admin_menu(admin_client):
    data = admin_client.get("/").data
    assert b"Admin" in data
    assert b"Departments" in data


def test_manager_sees_department_menu(manager_client):
    data = manager_client.get("/").data
    assert b"Department" in data
    assert b">Admin<" not in data


def test_employee_does_not_see_department_menu(employee_client):
    data = employee_client.get("/").data
    assert b"Leave Requests" not in data  # only inside Department dropdown
    assert b">Department<" not in data
