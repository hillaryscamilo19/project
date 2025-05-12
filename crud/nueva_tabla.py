# Ejemplo de operaciones CRUD para la nueva tabla
from sqlalchemy.orm import Session
from models.database_models import NuevaTabla
from models.schemas import NuevaTablaCreate

def get_nueva_tabla(db: Session, nueva_tabla_id: str):
    return db.query(NuevaTabla).filter(NuevaTabla.id == nueva_tabla_id).first()

def get_nuevas_tablas(db: Session, skip: int = 0, limit: int = 100, usuario_id: str = None):
    query = db.query(NuevaTabla)
    
    if usuario_id:
        query = query.filter(NuevaTabla.usuario_id == usuario_id)
    
    return query.offset(skip).limit(limit).all()

def create_nueva_tabla(db: Session, nueva_tabla: NuevaTablaCreate):
    db_nueva_tabla = NuevaTabla(
        nombre=nueva_tabla.nombre,
        descripcion=nueva_tabla.descripcion,
        usuario_id=nueva_tabla.usuario_id
    )
    db.add(db_nueva_tabla)
    db.commit()
    db.refresh(db_nueva_tabla)
    return db_nueva_tabla

def update_nueva_tabla(db: Session, nueva_tabla_id: str, nueva_tabla_data: dict):
    db_nueva_tabla = db.query(NuevaTabla).filter(NuevaTabla.id == nueva_tabla_id).first()
    
    if not db_nueva_tabla:
        return None
    
    for key, value in nueva_tabla_data.items():
        setattr(db_nueva_tabla, key, value)
    
    db.commit()
    db.refresh(db_nueva_tabla)
    return db_nueva_tabla

def delete_nueva_tabla(db: Session, nueva_tabla_id: str):
    db_nueva_tabla = db.query(NuevaTabla).filter(NuevaTabla.id == nueva_tabla_id).first()
    
    if not db_nueva_tabla:
        return None
    
    db.delete(db_nueva_tabla)
    db.commit()
    return db_nueva_tabla
