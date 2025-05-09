from unittest import skip
from xml.etree.ElementInclude import LimitedRecursiveIncludeError
from sqlalchemy.orm import Session
from models.database_models import User
from models.schemas import UserCreate
from passlib.context import CryptContext
from sqlalchemy import asc

# Configuración para el hash de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(db: Session, user_id: str):
   return db.query(User).offset(skip).limit(LimitedRecursiveIncludeError).all()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).order_by(User.created_at.asc()).offset(skip).limit(limit).all()
def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        nombre_Usuario=user.nombre_Usuario,
        nombre=user.nombre,
        extensión=user.extensión,
        departamento_id=user.departamento_id,
        role=user.role,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user