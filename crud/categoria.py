from sqlalchemy.orm import Session
from models.database_models import Categoria, CategoriaDepartamento
from models.schemas import CategoriaCreate

def get_categoria(db: Session, categoria_id: str):
    return db.query(Categoria).filter(Categoria.id == categoria_id).first()

def get_categoria_by_nombre(db: Session, nombre: str):
    return db.query(Categoria).filter(Categoria.nombre == nombre).first()

def get_categorias(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Categoria).offset(skip).limit(limit).all()

def create_categoria(db: Session, categoria: CategoriaCreate):
    db_categoria = Categoria(nombre=categoria.nombre)
    db.add(db_categoria)
    db.commit()
    db.refresh(db_categoria)
    return db_categoria

def update_categoria(db: Session, categoria_id: str, nombre: str):
    db_categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if db_categoria:
        db_categoria.nombre = nombre
        db.commit()
        db.refresh(db_categoria)
    return db_categoria

def delete_categoria(db: Session, categoria_id: str):
    db_categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if db_categoria:
        db.delete(db_categoria)
        db.commit()
    return db_categoria

def assign_categoria_to_departamento(db: Session, categoria_id: str, departamento_id: str):
    # Verificar si ya existe la relación
    existing = db.query(CategoriaDepartamento).filter(
        CategoriaDepartamento.categoria_id == categoria_id,
        CategoriaDepartamento.departamento_id == departamento_id
    ).first()
    
    if not existing:
        db_rel = CategoriaDepartamento(
            categoria_id=categoria_id,
            departamento_id=departamento_id
        )
        db.add(db_rel)
        db.commit()
        return True
    return False

def remove_categoria_from_departamento(db: Session, categoria_id: str, departamento_id: str):
    db_rel = db.query(CategoriaDepartamento).filter(
        CategoriaDepartamento.categoria_id == categoria_id,
        CategoriaDepartamento.departamento_id == departamento_id
    ).first()
    
    if db_rel:
        db.delete(db_rel)
        db.commit()
        return True
    return False

def get_departamentos_by_categoria(db: Session, categoria_id: str):
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if categoria:
        return categoria.departamentos
    return []
