"""
Seed script - Baltic IT Solutions SIA
Simulates ~2 months of real company activity (April 1 – May 20, 2026).

Includes: 10 employees, attendance records, leave requests,
          one department transfer, one position change.

Credentials:
  Administrator : aigars_berzins   / BalticAdmin#26
  IT Manager    : kristaps_liepins / ITProjMgr#26
  Finance Mgr   : ilze_ozola       / FinanceMgr#26
  HR Manager    : dace_kalnina     / HRMgmt#26
  Employees     : <username>       / Staff#2026
"""
import random
from datetime import date, timedelta, time as dtime
from .extensions import db
from .models import (
    Company, Department, Position,
    Employee, Manager, Administrator,
    Transfer, PositionChange,
    LeaveRequest, LeaveType, LeaveStatus,
    AttendanceRecord,
)

random.seed(42)

PERIOD_START = date(2026, 4, 1)
PERIOD_END   = date(2026, 5, 20)


# ── helpers ───────────────────────────────────────────────────────
def working_days(start, end):
    d = start
    while d <= end:
        if d.weekday() < 5:
            yield d
        d += timedelta(days=1)


def make_attendance(emp_id, on_date):
    start_min  = random.randint(480, 540)          # 8:00 – 9:00
    lunch      = random.choice([30, 45, 60])
    work_min   = random.randint(450, 480)           # 7.5 – 8.0 h
    finish_min = start_min + lunch + work_min
    return AttendanceRecord(
        employee_id=emp_id,
        date=on_date,
        start_time=dtime(start_min  // 60, start_min  % 60),
        lunch_break=lunch,
        finish_time=dtime(finish_min // 60, finish_min % 60),
    )


def leave_days(start, end):
    """Return set of working dates in [start, end]."""
    return set(working_days(start, end))


# ── public entry point ────────────────────────────────────────────
def seed_if_empty():
    if db.session.query(Company).first() is not None:
        return
    _seed()


# ── main seed ─────────────────────────────────────────────────────
def _seed():
    # ── Company ──────────────────────────────────────────────────
    company = Company(
        name="Baltic IT Solutions SIA",
        address="Aspazijas bulvāris 28, Rīga, LV-1050",
    )
    db.session.add(company)
    db.session.flush()

    # ── Departments ───────────────────────────────────────────────
    it_dept  = Department(code="IT",  name="Information Technology",
                          location="402", company_id=company.id)
    fin_dept = Department(code="FIN", name="Finance & Accounting",
                          location="205", company_id=company.id)
    hr_dept  = Department(code="HR",  name="Human Resources",
                          location="108", company_id=company.id)
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

    # ── Employees ─────────────────────────────────────────────────
    def make(cls, username, name, surname, dob, email, phone,
             dept, pos, password):
        e = cls(username=username, name=name, surname=surname,
                date_of_birth=dob,
                department_id=dept.id, position_id=pos.id)
        e.email = email
        e.phone_number = phone
        e.set_password(password)
        db.session.add(e)
        return e

    # 1 – admin
    aigars = make(Administrator, "aigars_berzins", "Aigars", "Bērziņš",
                  date(1982, 3, 15), "aigars.berzins@baltic-it.lv",
                  "+371 29 100 001", it_dept, pos_sysadmin, "BalticAdmin#26")
    db.session.flush()
    it_dept.manager_id = aigars.id

    # 2 – IT manager
    kristaps = make(Manager, "kristaps_liepins", "Kristaps", "Liepiņš",
                    date(1986, 7, 22), "kristaps.liepins@baltic-it.lv",
                    "+371 29 100 002", it_dept, pos_senior, "ITProjMgr#26")
    db.session.flush()
    it_dept.manager_id = kristaps.id

    # 3 – Finance manager
    ilze = make(Manager, "ilze_ozola", "Ilze", "Ozola",
                date(1983, 11, 5), "ilze.ozola@baltic-it.lv",
                "+371 29 100 003", fin_dept, pos_cfo, "FinanceMgr#26")
    db.session.flush()
    fin_dept.manager_id = ilze.id

    # 4 – HR manager
    dace = make(Manager, "dace_kalnina", "Dace", "Kalniņa",
                date(1988, 4, 18), "dace.kalnina@baltic-it.lv",
                "+371 29 100 004", hr_dept, pos_hr_mgr, "HRMgmt#26")
    db.session.flush()
    hr_dept.manager_id = dace.id

    # 5 – Senior developer (IT)
    janis = make(Employee, "janis_ozolins", "Jānis", "Ozoliņš",
                 date(1990, 9, 12), "janis.ozolins@baltic-it.lv",
                 "+371 29 100 005", it_dept, pos_senior, "Staff#2026")

    # 6 – Developer (IT) → promoted Apr 15
    anete = make(Employee, "anete_vitolina", "Anete", "Vītoliņa",
                 date(1995, 2, 28), "anete.vitolina@baltic-it.lv",
                 "+371 29 100 006", it_dept, pos_developer, "Staff#2026")

    # 7 – Junior developer (IT) → transferred to HR on Apr 10
    rihards = make(Employee, "rihards_skujins", "Rihards", "Skujiņš",
                   date(1999, 6, 10), "rihards.skujins@baltic-it.lv",
                   "+371 29 100 007", it_dept, pos_junior, "Staff#2026")

    # 8 – Financial analyst
    aiga = make(Employee, "aiga_freiberga", "Aiga", "Freiberga",
                date(1991, 12, 3), "aiga.freiberga@baltic-it.lv",
                "+371 29 100 008", fin_dept, pos_analyst, "Staff#2026")

    # 9 – Financial analyst
    toms = make(Employee, "toms_plavins", "Toms", "Pļaviņš",
                date(1993, 8, 25), "toms.plavins@baltic-it.lv",
                "+371 29 100 009", fin_dept, pos_analyst, "Staff#2026")

    # 10 – HR specialist
    inese = make(Employee, "inese_aboltina", "Inese", "Āboltiņa",
                 date(1996, 1, 17), "inese.aboltina@baltic-it.lv",
                 "+371 29 100 010", hr_dept, pos_hr_spec, "Staff#2026")

    db.session.flush()

    # ── Transfer: Rihards IT → HR  (Apr 10) ──────────────────────
    transfer_date = date(2026, 4, 10)
    db.session.add(Transfer(
        employee_id=rihards.id,
        source_department_id=it_dept.id,
        destination_department_id=hr_dept.id,
        date_time=transfer_date,
    ))
    rihards.department_id = hr_dept.id
    db.session.flush()

    # ── Position change: Anete Developer → Senior Dev  (Apr 15) ──
    db.session.add(PositionChange(
        employee_id=anete.id,
        previous_position_id=pos_developer.id,
        new_position_id=pos_senior.id,
        reason="Outstanding performance in Q1 2026. Consistently delivered ahead of schedule.",
        date_time=date(2026, 4, 15),
    ))
    anete.position_id = pos_senior.id
    db.session.flush()

    # ── Leave requests ────────────────────────────────────────────
    def leave(emp, ltype, start, end, submitted, status, supervisor):
        req = LeaveRequest(
            employee_id=emp.id,
            type=ltype,
            start_date=start,
            end_date=end,
            date_of_request=submitted,
            reason={
                LeaveType.VACATION:      "Annual vacation leave.",
                LeaveType.SICK_LEAVE:    "Medical certificate submitted.",
                LeaveType.PERSONAL_LEAVE:"Personal family matter.",
            }[ltype],
            status=status,
            supervisor_id=supervisor.id,
        )
        db.session.add(req)

    # Kristaps on vacation May 5-9 (supervisor = admin)
    leave(kristaps, LeaveType.VACATION,
          date(2026, 5, 5), date(2026, 5, 9),
          date(2026, 4, 28), LeaveStatus.APPROVED, aigars)

    # Jānis vacation Apr 21-25
    leave(janis, LeaveType.VACATION,
          date(2026, 4, 21), date(2026, 4, 25),
          date(2026, 4, 14), LeaveStatus.APPROVED, kristaps)

    # Anete sick leave Apr 28
    leave(anete, LeaveType.SICK_LEAVE,
          date(2026, 4, 28), date(2026, 4, 28),
          date(2026, 4, 28), LeaveStatus.APPROVED, kristaps)

    # Aiga sick leave May 2-3
    leave(aiga, LeaveType.SICK_LEAVE,
          date(2026, 5, 2), date(2026, 5, 3),
          date(2026, 5, 1), LeaveStatus.APPROVED, ilze)

    # Toms personal leave May 8
    leave(toms, LeaveType.PERSONAL_LEAVE,
          date(2026, 5, 8), date(2026, 5, 8),
          date(2026, 5, 6), LeaveStatus.APPROVED, ilze)

    # Inese personal leave May 15
    leave(inese, LeaveType.PERSONAL_LEAVE,
          date(2026, 5, 15), date(2026, 5, 15),
          date(2026, 5, 12), LeaveStatus.APPROVED, dace)

    # Rihards vacation May 26-30 (PENDING — future, supervisor now Dace/HR)
    leave(rihards, LeaveType.VACATION,
          date(2026, 5, 26), date(2026, 5, 30),
          date(2026, 5, 19), LeaveStatus.PENDING, dace)

    # Toms rejected request (Apr 17 — short notice)
    rej = LeaveRequest(
        employee_id=toms.id,
        type=LeaveType.PERSONAL_LEAVE,
        start_date=date(2026, 4, 18),
        end_date=date(2026, 4, 18),
        date_of_request=date(2026, 4, 17),
        reason="Need to handle a personal matter.",
        status=LeaveStatus.REJECTED,
        supervisor_id=ilze.id,
    )
    db.session.add(rej)
    db.session.flush()

    # ── Attendance records ────────────────────────────────────────
    # Days each person was on approved leave (skip attendance for those days)
    absent = {
        kristaps.id: leave_days(date(2026, 5, 5),  date(2026, 5, 9)),
        janis.id:    leave_days(date(2026, 4, 21), date(2026, 4, 25)),
        anete.id:    leave_days(date(2026, 4, 28), date(2026, 4, 28)),
        aiga.id:     leave_days(date(2026, 5, 2),  date(2026, 5, 3)),
        toms.id:     leave_days(date(2026, 5, 8),  date(2026, 5, 8)),
        inese.id:    leave_days(date(2026, 5, 15), date(2026, 5, 15)),
    }

    all_employees = [aigars, kristaps, ilze, dace,
                     janis, anete, rihards, aiga, toms, inese]

    for emp in all_employees:
        off_days = absent.get(emp.id, set())
        # ~5% chance of missing a random day (illness, WFH not recorded, etc.)
        skip_extra = set(
            d for d in working_days(PERIOD_START, PERIOD_END)
            if random.random() < 0.05
        )
        for day in working_days(PERIOD_START, PERIOD_END):
            if day in off_days or day in skip_extra:
                continue
            db.session.add(make_attendance(emp.id, day))

    db.session.commit()
