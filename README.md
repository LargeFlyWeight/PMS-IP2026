# Personnel Management System (PMS-IP2026)

Course project — Software Engineering, TSI.
Flask + SQLAlchemy + Flask-Login, SQLite, Docker.

## OOP highlights

- **Inheritance**: `Employee → Manager → Administrator` (SQLAlchemy single-table polymorphism in `pms/models.py`).
- **Encapsulation**: private columns `_email`, `_phone_number`, `_password_hash` exposed via property setters with validation.
- **Polymorphism**: `auto_approve_leave()`, `can_view_employee()`, `can_manage_department()`, `supervisor()` are overridden in subclasses.
- **Composition / Aggregation**: `Company` ⟶ `Department` (composition, cascade delete); `Department` ⟶ `Employee` (aggregation).
- **Layered architecture** (matches sequence diagrams in milestone 5): Controller (Flask blueprint) → Service → Repository → SQLAlchemy / DB.

## Run locally (no Docker)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Open <http://localhost:8000>.

## Run with Docker

```bash
docker compose up --build
```

## Default accounts

| Username    | Password   | Role          |
|-------------|------------|---------------|
| adminPMS    | Ip-2026!   | Administrator |
| mgr_eng     | manager1   | Manager (Engineering) |
| mgr_sales   | manager1   | Manager (Sales) |
| employee1   | employee1  | Employee (Engineering) |
| employee2   | employee1  | Employee (Engineering) |
| employee3   | employee1  | Employee (Sales) |

## Deploy to Fly.io

```bash
fly launch --no-deploy --copy-config
fly volumes create pms_data --size 1 --region fra
fly deploy
```

The SQLite file lives in `/data/pms.db` on the volume.

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
  static/style.css   Minimal pistachio styling
run.py
Dockerfile
docker-compose.yml
fly.toml
```
