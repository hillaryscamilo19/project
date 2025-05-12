from pydantic import BaseModel
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
import uuid
from models.base import Base  # Importar Base desde models.base

import uuid


# Importar Base desde database sin importar Department
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    nombre_Usuario = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    extensión = Column(String(50), nullable=True)
    nombre = Column(String(255), nullable=False)
    departamento_id = Column(String(36), ForeignKey("Departamentos.id"))  
    role = Column(String(20), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    tickets_created = relationship("Ticket", back_populates="requester", foreign_keys="Ticket.requested_by")
    tickets_assigned = relationship("Ticket", back_populates="assignee", foreign_keys="Ticket.assigned_to")
    comments = relationship("Comment", back_populates="user")
    departamento_rel = relationship("Department", back_populates="users")

class Comment(Base):
    __tablename__ = 'comments'
    
    id: Mapped[str] = mapped_column(primary_key=True, index=True)  # Ajusta según tipo de id
    content: Mapped[str]  # Usa Mapped[] en lugar de solo str
    ticket_id: Mapped[int]
    user_id: Mapped[str]  # O el tipo adecuado para el user_id
    created_at: Mapped[datetime]
# Tabla de tickets (actualizada con nuevas relaciones)
class Ticket(Base):
    __tablename__ = "ticket"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    descripcion = Column(Text)
    departamento_id = Column(String(36), ForeignKey("departments.id"))
    categoria_id = Column(String(36), ForeignKey("categoria.id"))
    user_id = Column(String(36), ForeignKey("users.id"))
    menssage_id = Column(String(36), ForeignKey("mensage.id"), nullable=True)
    status = Column(String(20))  # abierto, en progreso, en espera, resuelto, cerrado
    assigned_to = Column(String(36), ForeignKey("users.id"), nullable=True)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    requester = relationship("User", back_populates="tickets_created", foreign_keys=[user_id])
    assignee = relationship("User", back_populates="tickets_assigned", foreign_keys=[assigned_to])
    comments = relationship("Comment", back_populates="ticket", cascade="all, delete-orphan")
    department_rel = relationship("Department", back_populates="tickets")
    categoria = relationship("Categoria", back_populates="tickets")
    mensaje = relationship("Mensaje", back_populates="tickets")
    attachments = relationship("Attachment", back_populates="ticket", cascade="all, delete-orphan")


# Tabla de categorías
class Categoria(Base):
    __tablename__ = "categoria"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    nombre = Column(String(255), nullable=False, unique=True)

    # Relaciones
    tickets = relationship("Ticket", back_populates="categoria")
    departamentos = relationship("Department", secondary="CategoriaDepartamento", back_populates="categorias")

    # Tabla de asociación entre Categoría y Departamento
class CategoriaDepartamento(Base):
    __tablename__ = "CategoriaDepartamento"

    categoria_id = Column(String(36), ForeignKey("categoria.id"), primary_key=True)
    departamento_id = Column(String(36), ForeignKey("departments.id"), primary_key=True)

# Tabla de mensajes
class Mensaje(Base):
    __tablename__ = "mensage"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    mensaje = Column(Text, nullable=False)
    users_id = Column(String(36), ForeignKey("users.id"))
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    user = relationship("User", back_populates="mensajes")

class MyBaseModel(BaseModel):
    model_config = {
        "arbitrary_types_allowed": True
    }
# Esquemas para Comment
class CommentBase(BaseModel):
    content: str
    ticket_id: int

class CommentCreate(CommentBase):
    pass

class CommentResponse(CommentBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True
        
        
    __tablename__ = "attachements"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    file_extension: Mapped[str] = mapped_column(String(10))
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"))
    # Relaciones
    ticket: Mapped["Ticket"] = relationship("Ticket", back_populates="comments")
