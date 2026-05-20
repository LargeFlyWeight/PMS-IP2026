"""
Seed script - Baltic IT Solutions SIA
10 people with realistic Latvian names across 3 departments.

Credentials (change after first login):
  Administrator : aigars_berzins  / BalticAdmin#26
  Managers      : kristaps_liepins / ITProjMgr#26
                  ilze_ozola       / FinanceMgr#26
                  dace_kalnina     / HRMgmt#26
  Employees     : <username>       / Staff#2026
"""
from datetime import date
from .extensions import db
from .models import (
    Company, Department, Position,
    Employee, Manager, Administrator,
)


def seed_if_empty():
    if db.session.query(Company).first() is not None:
        return
    _seed()


def _seed():
    # ── Company ──────────────────────────────────────────────────
    company = Company(
        name="Baltic IT Solutions SIA",
        address="Aspazijas bulvāris 28, Rīga, LV-1050",
    )
    db.session.add(company)
    db.session.flush()

    # ── Departments ───────────────────────────────────────────────
    it_dept = Department(
        code="IT", name="Information Technology",
        location="402", company_id=company.id,
    )
    fin_dept = Department(
        code="FIN", name="Finance & Accounting",
        location="205", company_id=company.id,
    )
    hr_dept = Department(
        code="HR", name="Human Resources",
        location="108", company_id=company.id,
    )
    db.session.add_all([it_dept, fin_dept, hr_dept])
    db.session.flush()

    # ── Positions ─────────────────────────────────────────────────
    pos_sysadmin  = Position(title="System Administrator",
                             salary_grade="A1",
                             description="Full system access and IT infrastructure management.")
    pos_senior    = Position(title="Senior Software Developer",
                             salary_grade="A2",
                             description="Design and develop core system modules.")
    pos_developer = Position(title="Software Developer",
                             salary_grade="A3",
                             description="Implement features and maintain existing codebase.")
    pos_junior    = Position(title="Junior Software Developer",
                             salary_grade="A4",
                             description="Support development tasks under senior guidance.")
    pos_cfo       = Position(title="Chief Financial Officer",
                             salary_grade="B1",
                             description="Oversee financial strategy and reporting.")
    pos_analyst   = Position(title="Financial Analyst",
                             salary_grade="B2",
                             description="Budgeting, forecasting and financial analysis.")
    pos_hr_mgr    = Position(title="HR Manager",
                             salary_grade="C1",
                             description="Talent acquisition, onboarding and HR policy.")
    pos_hr_spec   = Position(title="HR Specialist",
                             salary_grade="C2",
                             description="Employee records, leave administration and payroll support.")
    db.session.add_all([
        pos_sysadmin, pos_senior, pos_developer, pos_junior,
        pos_cfo, pos_analyst, pos_hr_mgr, pos_hr_spec,
    ])
    db.session.flush()

    # ── Helper ────────────────────────────────────────────────────
    def emp(cls, username, name, surname, dob, email, phone,
            department, position, password):
        e = cls(
            username=username,
            name=name,
            surname=surname,
            date_of_birth=dob,
            department_id=department.id,
            position_id=position.id,
        )
        e.email = email
        e.phone_number = phone
        e.set_password(password)
        db.session.add(e)
        return e

    # ── 1  Administrator ──────────────────────────────────────────
    aigars = emp(
        Administrator,
        "aigars_berzins", "Aigars", "Bērziņš",
        date(1982, 3, 15),
        "aigars.berzins@baltic-it.lv", "+371 29 100 001",
        it_dept, pos_sysadmin,
        "BalticAdmin#26",
    )
    db.session.flush()
    it_dept.manager_id = aigars.id  # temporary until Kristaps is flushed

    # ── 2  IT Manager ─────────────────────────────────────────────
    kristaps = emp(
        Manager,
        "kristaps_liepins", "Kristaps", "Liepiņš",
        date(1986, 7, 22),
        "kristaps.liepins@baltic-it.lv", "+371 29 100 002",
        it_dept, pos_senior,
        "ITProjMgr#26",
    )
    db.session.flush()
    it_dept.manager_id = kristaps.id

    # ── 3  Finance Manager ────────────────────────────────────────
    ilze = emp(
        Manager,
        "ilze_ozola", "Ilze", "Ozola",
        date(1983, 11, 5),
        "ilze.ozola@baltic-it.lv", "+371 29 100 003",
        fin_dept, pos_cfo,
        "FinanceMgr#26",
    )
    db.session.flush()
    fin_dept.manager_id = ilze.id

    # ── 4  HR Manager ─────────────────────────────────────────────
    dace = emp(
        Manager,
        "dace_kalnina", "Dace", "Kalniņa",
        date(1988, 4, 18),
        "dace.kalnina@baltic-it.lv", "+371 29 100 004",
        hr_dept, pos_hr_mgr,
        "HRMgmt#26",
    )
    db.session.flush()
    hr_dept.manager_id = dace.id

    # ── 5  Senior Developer ───────────────────────────────────────
    emp(
        Employee,
        "janis_ozolins", "Jānis", "Ozoliņš",
        date(1990, 9, 12),
        "janis.ozolins@baltic-it.lv", "+371 29 100 005",
        it_dept, pos_senior,
        "Staff#2026",
    )

    # ── 6  Software Developer ─────────────────────────────────────
    emp(
        Employee,
        "anete_vitolina", "Anete", "Vītoliņa",
        date(1995, 2, 28),
        "anete.vitolina@baltic-it.lv", "+371 29 100 006",
        it_dept, pos_developer,
        "Staff#2026",
    )

    # ── 7  Junior Developer ───────────────────────────────────────
    emp(
        Employee,
        "rihards_skujins", "Rihards", "Skujiņš",
        date(1999, 6, 10),
        "rihards.skujins@baltic-it.lv", "+371 29 100 007",
        it_dept, pos_junior,
        "Staff#2026",
    )

    # ── 8  Financial Analyst ──────────────────────────────────────
    emp(
        Employee,
        "aiga_freiberga", "Aiga", "Freiberga",
        date(1991, 12, 3),
        "aiga.freiberga@baltic-it.lv", "+371 29 100 008",
        fin_dept, pos_analyst,
        "Staff#2026",
    )

    # ── 9  Financial Analyst ──────────────────────────────────────
    emp(
        Employee,
        "toms_plavins", "Toms", "Pļaviņš",
        date(1993, 8, 25),
        "toms.plavins@baltic-it.lv", "+371 29 100 009",
        fin_dept, pos_analyst,
        "Staff#2026",
    )

    # ── 10  HR Specialist ─────────────────────────────────────────
    emp(
        Employee,
        "inese_aboltina", "Inese", "Āboltiņa",
        date(1996, 1, 17),
        "inese.aboltina@baltic-it.lv", "+371 29 100 010",
        hr_dept, pos_hr_spec,
        "Staff#2026",
    )

    db.session.commit()
