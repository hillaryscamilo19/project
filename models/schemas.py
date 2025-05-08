
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime

# Esquemas para Usuario
# Esquemas para Usuario
class UserBase(BaseModel):
    email: EmailStr
    nombre_Usuario: str
    nombre: str
    extensión: Optional[str] = None
    departamento_id: str  # Usamos el ID del departamento
    role: str = Field(..., pattern="^(usuario|soporte|administrador)$")

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: str
    created_at: datetime

    class Config:
        orm_mode = True


# Esquemas para Autenticación
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Esquemas para Ticket
# Esquemas para Ticket
class TicketBase(BaseModel):
    title: str = Field(..., min_length=5)
    description: str = Field(..., min_length=10)
    departamento_id: str  # Usamos el ID del departamento
    priority: str = Field(..., pattern="^(baja|media|alta|crítica)$")

class TicketCreate(TicketBase):
    pass

class TicketUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5)
    description: Optional[str] = Field(None, min_length=10)
    priority: Optional[str] = Field(None, pattern="^(baja|media|alta|crítica)$")
    status: Optional[str] = Field(None, pattern="^(abierto|en progreso|en espera|resuelto|cerrado)$")
    assigned_to: Optional[str] = None


# Esquemas para Comentario
class CommentBase(BaseModel):
    content: str = Field(..., min_length=1)

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: str
    ticket_id: str
    user_id: str
    created_at: datetime

    class Config:
        orm_mode = True

# Esquema completo de Ticket con comentarios
class Ticket(TicketBase):
    id: str
    status: str
    requested_by: str
    assigned_to: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    comments: List[Comment] = []

    class Config:
        orm_mode = True

# Esquemas para Departamento
class DepartmentBase(BaseModel):
    name: str = Field(..., min_length=2)
    description: Optional[str] = None

class DepartmentCreate(DepartmentBase):
    pass

class Department(DepartmentBase):
    id: str
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True