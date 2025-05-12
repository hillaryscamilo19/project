from uuid import UUID
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Mapped
from pydantic import BaseModel, Field, EmailStr
from pydantic import BaseModel
from models.schemas import BaseModelWithConfig


# Configuración base para Pydantic V2
class MyModel(BaseModel):
    id: Mapped[int]
    class Config:
        from_attributes = True 
# Esquemas para Usuario
class UserBase(BaseModelWithConfig):
    email: EmailStr
    nombre_Usuario: str
    nombre: str
    extensión: Optional[str] = None
    departamento_id: Optional[str]
    role: str = Field(..., pattern="^(usuario|soporte|administrador)$")

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: UUID
    created_at: datetime

# Esquemas para Autenticación
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Esquemas para Comentario
class CommentBase(BaseModel):
    content: str = Field(..., min_length=1)
    ticket_id: str

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: UUID
    user_id: str
    created_at: datetime

# Esquemas para Departamento
class DepartmentBase(BaseModel):
    nombre: str = Field(..., min_length=2)

class DepartmentCreate(DepartmentBase):
    pass

class Department(DepartmentBase):
    id: UUID
    create_at: Optional[datetime] = None

# Esquemas para Categoría
class CategoriaBase(BaseModel):
    nombre: str

class CategoriaCreate(CategoriaBase):
    pass

class Categoria(CategoriaBase):
    id: UUID

# Esquemas para CategoriaDepartamento
class CategoriaDepartamentoBase(BaseModel):
    categoria_id: UUID
    departamento_id: UUID

class CategoriaDepartamentoCreate(CategoriaDepartamentoBase):
    pass

class CategoriaDepartamento(CategoriaDepartamentoBase):
    pass

# Esquemas para Mensaje
class MensajeBase(BaseModel):
    mensaje: str
    users_id: UUID

class MensajeCreate(MensajeBase):
    pass

class Mensaje(MensajeBase):
    id: UUID
    createdAt: datetime
    updatedAt: datetime

# Esquemas para Attachment
class AttachmentBase(BaseModel):
    file_name: str
    file_path: str
    file_extension: Optional[str] = None

class AttachmentCreate(AttachmentBase):
    ticket_id: str

class Attachment(AttachmentBase):
    id: UUID
    ticket_id: str

# Esquemas para Ticket
class TicketBase(BaseModel):
    title: str = Field(..., min_length=5)
    description: str = Field(..., min_length=10)
    departamento_id: str
    priority: str = Field(..., pattern="^(baja|media|alta|crítica)$")

class TicketCreate(TicketBase):
    pass

class TicketUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5)
    description: Optional[str] = Field(None, min_length=10)
    priority: Optional[str] = Field(None, pattern="^(baja|media|alta|crítica)$")
    status: Optional[str] = Field(None, pattern="^(abierto|en progreso|en espera|resuelto|cerrado)$")
    assigned_to: Optional[str] = None

class Ticket(TicketBase):
    id: UUID
    status: str
    requested_by: str
    assigned_to: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    comments: List[Comment] = []

    class Config:
        from_attributes = True

# Actualizar referencias circulares
Ticket.update_forward_refs()
