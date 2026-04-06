import os
from datetime import date
from .extensions import db
from .models import Company, Department, Position, Employee, Manager, Administrator


def seed_if_empty():
    if db.session.query(Company).first() is not None:
        return

    full = os.environ.get("PMS_SEED", "minimal").lower() == "full"

    company = Company(name="TSI Corp", address="Lomonosova 1, Riga")
    db.session.add(company)
    db.session.flush()

    hr = Department(code="HQ", name="Headquarters", location="101", company_id=company.id)
    db.session.add(hr)
    db.session.flush()

    p_admin = Position(title="System Administrator", salary_grade="A1",
                       description="Full system access")
    db.session.add(p_admin)
    db.session.flush()

    admin = Administrator(
        username="adminPMS",
        name="System",
        surname="Administrator",
        date_of_birth=date(1990, 1, 1),
        department_id=hr.id,
        position_id=p_admin.id,
    )
    admin.email = "admin@tsi.lv"
    admin.phone_number = "+371 20000000"
    admin.set_password("Ip-2026!")
    db.session.add(admin)
    db.session.flush()

    hr.manager_id = admin.id

    if not full:
        db.session.commit()
        return

    eng = Department(code="ENG", name="Engineering", location="402", company_id=company.id)
    sales = Department(code="SAL", name="Sales", location="551", company_id=company.id)
    db.session.add_all([eng, sales])
    db.session.flush()

    p_lead = Position(title="Team Lead", salary_grade="B1", description="Team management")
    p_dev = Position(title="Developer", salary_grade="B2", description="Software development")
    p_sales = Position(title="Sales Specialist", salary_grade="C1", description="Sales operations")
    db.session.add_all([p_lead, p_dev, p_sales])
    db.session.flush()

    mgr_eng = Manager(username="mgr_eng", name="Anna", surname="Berzina",
                      date_of_birth=date(1988, 5, 12),
                      department_id=eng.id, position_id=p_lead.id)
    mgr_eng.email = "anna@tsi.lv"
    mgr_eng.phone_number = "+371 20000001"
    mgr_eng.set_password("manager1")
    db.session.add(mgr_eng)

    mgr_sales = Manager(username="mgr_sales", name="Janis", surname="Ozols",
                        date_of_birth=date(1985, 9, 3),
                        department_id=sales.id, position_id=p_lead.id)
    mgr_sales.email = "janis@tsi.lv"
    mgr_sales.phone_number = "+371 20000002"
    mgr_sales.set_password("manager1")
    db.session.add(mgr_sales)

    emp1 = Employee(username="employee1", name="Peteris", surname="Kalnins",
                    date_of_birth=date(1995, 3, 15),
                    department_id=eng.id, position_id=p_dev.id)
    emp1.email = "peteris@tsi.lv"
    emp1.phone_number = "+371 20000003"
    emp1.set_password("employee1")
    db.session.add(emp1)

    emp2 = Employee(username="employee2", name="Liga", surname="Vitola",
                    date_of_birth=date(1996, 7, 22),
                    department_id=eng.id, position_id=p_dev.id)
    emp2.email = "liga@tsi.lv"
    emp2.phone_number = "+371 20000004"
    emp2.set_password("employee1")
    db.session.add(emp2)

    emp3 = Employee(username="employee3", name="Maris", surname="Skujins",
                    date_of_birth=date(1993, 11, 8),
                    department_id=sales.id, position_id=p_sales.id)
    emp3.email = "maris@tsi.lv"
    emp3.phone_number = "+371 20000005"
    emp3.set_password("employee1")
    db.session.add(emp3)

    db.session.flush()
    eng.manager_id = mgr_eng.id
    sales.manager_id = mgr_sales.id

    db.session.commit()
