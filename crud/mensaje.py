from sqlalchemy.orm import Session
from models.database_models import Mensaje
from models.schemas import MensajeCreate
from datetime import datetime

def get_mensaje(db: Session, mensaje_id: str):
    return db.query(Mensaje).filter(Mensaje.id == mensaje_id).first()

def get_mensajes_by_user(db: Session, user_id: str, skip: int = 0, limit: int = 100):
    return db.query(Mensaje).filter(Mensaje.users_id == user_id).offset(skip).limit(limit).all()

def get_mensajes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Mensaje).offset(skip).limit(limit).all()

def create_mensaje(db: Session, mensaje: MensajeCreate):
    db_mensaje = Mensaje(
        mensaje=mensaje.mensaje,
        users_id=mensaje.users_id
    )
    db.add(db_mensaje)
    db.commit()
    db.refresh(db_mensaje)
    return db_mensaje

def update_mensaje(db: Session, mensaje_id: str, mensaje_text: str):
    db_mensaje = db.query(Mensaje).filter(Mensaje.id == mensaje_id).first()
    if db_mensaje:
        db_mensaje.mensaje = mensaje_text
        db_mensaje.updatedAt = datetime.utcnow()
        db.commit()
        db.refresh(db_mensaje)
    return db_mensaje

def delete_mensaje(db: Session, mensaje_id: str):
    db_mensaje = db.query(Mensaje).filter(Mensaje.id == mensaje_id).first()
    if db_mensaje:
        db.delete(db_mensaje)
        db.commit()
    return db_mensaje
