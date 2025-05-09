from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
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
    departamento_id = Column(String(36), ForeignKey("Departamentos.id"))  # ✅ Cambio aquí
    role = Column(String(20), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    tickets_created = relationship("Ticket", back_populates="requester", foreign_keys="Ticket.requested_by")
    tickets_assigned = relationship("Ticket", back_populates="assignee", foreign_keys="Ticket.assigned_to")
    comments = relationship("Comment", back_populates="user")
    departamento_rel = relationship("Department", back_populates="users")

class Department(Base):
    __tablename__ = "Departamentos"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    nombre = Column(String(255), unique=True)
    decripcion = Column(Text, nullable=True)
    create_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    tickets = relationship("Ticket", back_populates="department_rel")
    users = relationship("User", back_populates="departamento_rel")

class Ticket(Base):
    __tablename__ = "Tickets"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    departamento = Column(String(36), ForeignKey("Departamentos.id"))
    priority = Column(String(20), nullable=False)  # baja, media, alta, crítica
    status = Column(String(20), nullable=False)  # abierto, en progreso, en espera, resuelto, cerrado
    requested_by = Column(String(36), ForeignKey("users.id"))
    assigned_to = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    requester = relationship("User", back_populates="tickets_created", foreign_keys=[requested_by])
    assignee = relationship("User", back_populates="tickets_assigned", foreign_keys=[assigned_to])
    comments = relationship("Comment", back_populates="ticket", cascade="all, delete-orphan")
    department_rel = relationship("Department", back_populates="tickets")

class Comment(Base):
    __tablename__ = "Comments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    content = Column(Text, nullable=False)
    ticket_id = Column(String(36), ForeignKey("Tickets.id", ondelete="CASCADE"))
    user_id = Column(String(36), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    ticket = relationship("Ticket", back_populates="comments")
    user = relationship("User", back_populates="comments")