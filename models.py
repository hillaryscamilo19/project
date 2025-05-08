from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    nombre_Usuario: str
    extensión: str
    department: str
    nombre: str
    role: str = Field(..., pattern="^(usuario|soporte|administrador)$")

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: str
    created_at: datetime

    class Config:
        orm_mode = True

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class TicketBase(BaseModel):
    title: str = Field(..., min_length=5)
    description: str = Field(..., min_length=10)
    department: str
    priority: str = Field(..., pattern="^(baja|media|alta|crítica)$")

class TicketCreate(TicketBase):
    pass

class Comment(BaseModel):
    id: str
    content: str
    user_id: str
    created_at: datetime

class Ticket(TicketBase):
    id: str
    status: str = Field(..., pattern="^(abierto|en progreso|en espera|resuelto|cerrado)$")
    requested_by: str
    assigned_to: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    comments: List[Comment] = []

    class Config:
        orm_mode = True

class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1)

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
