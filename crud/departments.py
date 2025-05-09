from sqlalchemy.orm import Session
from models.database_models import Department
from models.schemas import DepartmentCreate

def get_department(db: Session, department_id: str):
    return db.query(Department).filter(Department.id == department_id).first()

def get_department_by_name(db: Session, name: str):
    return db.query(Department).filter(Department.name == name).first()

def get_departments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Department).order_by(Department.id).offset(skip).limit(limit).all()


def create_department(db: Session, department: DepartmentCreate):
    db_department = Department(
        name=department.name,
        description=department.description
    )
    db.add(db_department)
    db.commit()
    db.refresh(db_department)
    return db_department