from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import timedelta

from database import engine, get_db, Base
from schemas.schemas import User, Department, Ticket, Comment
from models.schemas import (
    User as UserSchema,
    UserCreate,
    Token,
    Ticket as TicketSchema,
    TicketCreate,
    TicketUpdate,
    Comment as CommentSchema,
    CommentCreate,
    Department as DepartmentSchema,
    DepartmentCreate
)
from crud import users, tickets, departments
from auth.jwt import create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES

# Crear las tablas en la base de datos (comentar si ya existen)
# Base.metadata.create_all(bind=engine)

# Inicializar la aplicación FastAPI
app = FastAPI(
    title="Sistema de Tickets",
    description="API para gestionar tickets y solicitudes internas con SQL Server",
    version="1.0.0"
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint de autenticación
@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = users.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoints de usuarios
@app.post("/users/", response_model=UserSchema)
async def create_user_endpoint(user: UserCreate, db: Session = Depends(get_db)):
    db_user = users.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    return users.create_user(db=db, user=user)

@app.get("/users/me/", response_model=UserSchema)
async def read_users_me(
    current_user: User = Depends(get_current_user)
):
    return current_user

@app.get("/users/", response_model=List[UserSchema])
async def read_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "administrador":
        raise HTTPException(status_code=403, detail="No tiene permisos para ver todos los usuarios")
    return users.get_users(db, skip=skip, limit=limit)

# Endpoints de tickets
@app.post("/tickets/", response_model=TicketSchema)
async def create_ticket_endpoint(
    ticket: TicketCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return tickets.create_ticket(db=db, ticket=ticket, user_id=current_user.id)

@app.get("/tickets/", response_model=List[TicketSchema])
async def read_tickets(
    skip: int = 0, 
    limit: int = 100, 
    status: Optional[str] = None,
    departamento: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return tickets.get_tickets(
        db, 
        skip=skip, 
        limit=limit, 
        status=status,
        departamento=departamento,
        user_id=current_user.id,
        role=current_user.role
    )

@app.get("/tickets/{ticket_id}", response_model=TicketSchema)
async def read_ticket(
    ticket_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_ticket = tickets.get_ticket(db, ticket_id=ticket_id)
    if db_ticket is None:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    
    # Verificar permisos
    if current_user.role == "usuario" and db_ticket.requested_by != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene permisos para ver este ticket")
    elif current_user.role == "soporte" and db_ticket.departamento != current_user.departamento and db_ticket.assigned_to != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene permisos para ver este ticket")
    
    return db_ticket

@app.patch("/tickets/{ticket_id}", response_model=TicketSchema)
async def update_ticket_endpoint(
    ticket_id: str, 
    ticket_update: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_ticket = tickets.get_ticket(db, ticket_id=ticket_id)
    if db_ticket is None:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    
    # Verificar permisos
    if current_user.role == "usuario" and db_ticket.requested_by != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene permisos para actualizar este ticket")
    
    updated_ticket = tickets.update_ticket(db, ticket_id, ticket_update)
    return updated_ticket

@app.post("/tickets/{ticket_id}/comments/", response_model=CommentSchema)
async def create_comment_endpoint(
    ticket_id: str, 
    comment: CommentCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_ticket = tickets.get_ticket(db, ticket_id=ticket_id)
    if db_ticket is None:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    
    # Verificar permisos
    if current_user.role == "usuario" and db_ticket.requested_by != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene permisos para comentar en este ticket")
    elif current_user.role == "soporte" and db_ticket.departamento != current_user.departamento and db_ticket.assigned_to != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene permisos para comentar en este ticket")
    
    return tickets.add_comment(db, ticket_id, comment, current_user.id)

# Endpoints de departamentos
@app.get("/departments/", response_model=List[DepartmentSchema])
async def read_departments(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    return departments.get_departments(db, skip=skip, limit=limit)

@app.post("/departments/", response_model=DepartmentSchema)
async def create_department_endpoint(
    department: DepartmentCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "administrador":
        raise HTTPException(status_code=403, detail="No tiene permisos para crear departamentos")
    
    db_department = departments.get_department_by_name(db, name=department.name)
    if db_department:
        raise HTTPException(status_code=400, detail="Ya existe un departamento con ese nombre")
    
    return departments.create_department(db=db, department=department)

# Punto de entrada para ejecutar la aplicación
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)