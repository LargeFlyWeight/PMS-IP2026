# Personnel Management System (PMS-IP2026)

Course project — Software Engineering, Transport and Telecommunication Institute.
Flask + SQLAlchemy + Flask-Login, SQLite. Docker for local dev, PythonAnywhere for hosting.

## OOP highlights

- **Inheritance**: `Employee → Manager → Administrator` via SQLAlchemy single-table polymorphism in `pms/models.py`.
- **Encapsulation**: private columns `_email`, `_phone_number`, `_password_hash` exposed via property setters with validation.
- **Polymorphism**: `auto_approve_leave()`, `can_view_employee()`, `can_manage_department()`, `supervisor()` are overridden in subclasses.
- **Composition / Aggregation**: `Company` ⟶ `Department` (composition, cascade delete); `Department` ⟶ `Employee` (aggregation).
- **Layered architecture** matching milestone-5 sequence diagrams: Controller (Flask blueprint) → Service → Repository → SQLAlchemy / DB.

## Local development

### Plain Python
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PMS_SEED=full python run.py
```
Open <http://localhost:8000>.

### Docker
```bash
docker compose up --build
```

### Default accounts (full seed)

| Username    | Password   | Role          |
|-------------|------------|---------------|
| adminPMS    | Ip-2026!   | Administrator |
| mgr_eng     | manager1   | Manager (Engineering) |
| mgr_sales   | manager1   | Manager (Sales) |
| employee1/2 | employee1  | Employee (Engineering) |
| employee3   | employee1  | Employee (Sales) |

In production (`PMS_SEED=minimal`, default) only `adminPMS` is created.

## Tests

```bash
python -m pytest tests/ -v
```
43 tests covering all use cases from milestone 3.

## Production deployment — PythonAnywhere

1. Sign up at <https://www.pythonanywhere.com/registration/register/beginner/> (free, no card required).
2. Open **Consoles → Bash** and clone the repo:
   ```bash
   git clone https://github.com/LargeFlyWeight/PMS-IP2026.git
   cd PMS-IP2026
   mkvirtualenv pms --python=python3.12
   pip install -r requirements.txt
   ```
3. Open **Web → Add a new web app → Manual configuration → Python 3.12**.
4. Configure paths in the Web tab:
   - **Source code:** `/home/<user>/PMS-IP2026`
   - **Working directory:** `/home/<user>/PMS-IP2026`
   - **Virtualenv:** `/home/<user>/.virtualenvs/pms`
5. Edit the WSGI file (link in Web tab) — replace its contents with:
   ```python
   import os, sys
   project_home = "/home/<user>/PMS-IP2026"
   if project_home not in sys.path:
       sys.path.insert(0, project_home)

   os.environ["PMS_SECRET_KEY"] = "<long-random-string>"
   os.environ["PMS_DB_PATH"] = "/home/<user>/pms.db"
   os.environ["PMS_SEED"] = "minimal"

   from wsgi import application
   ```
6. Press **Reload** in the Web tab.

App is live at `https://<user>.pythonanywhere.com`.

### Updating after a code change
```bash
cd ~/PMS-IP2026
git pull
```
Then **Reload** in the Web tab.

## Project layout

```
pms/
  __init__.py        Flask factory + blueprint registration
  extensions.py      db, login_manager
  models.py          Domain + ORM (Company, Department, Position,
                     Employee→Manager→Administrator, Transfer,
                     PositionChange, LeaveRequest, AttendanceRecord)
  repositories.py    Data-access layer
  services.py        Business rules and validation
  seed.py            Initial company / departments / users
  routes/            Flask blueprints (one per use-case group)
  templates/         Jinja templates
  static/style.css   Pistachio styling
tests/               pytest suite
run.py               Local dev entry point
wsgi.py              Production WSGI entry point (PythonAnywhere)
Dockerfile           Local containerized dev
docker-compose.yml
```
