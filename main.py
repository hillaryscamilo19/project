from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
from pathlib import Path
from config import BaseModelWithConfig
from database import get_db

from schemas.schemas import (
    User, UserCreate, Token,
    Ticket, TicketCreate, TicketUpdate,
    Comment, CommentCreate,
    Department, DepartmentCreate,
    Categoria, CategoriaCreate,
    CategoriaDepartamento, CategoriaDepartamentoCreate,
    Mensaje, MensajeCreate,
    Attachment, AttachmentCreate
)
from crud import users, tickets, comments, departments, categoria, mensaje, attachment
from auth.jwt import create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi import Form
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

# Crear la instancia de FastAPI
app = FastAPI(
    title="Sistema de Tickets",
    description="API para gestionar tickets y solicitudes internas",
    version="1.0.0"
)

# Configuración CORS
from fastapi.middleware.cors import CORSMiddleware
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
@app.post("/users/", response_model=User)
async def create_user_endpoint(user: UserCreate, db: Session = Depends(get_db)):
    db_user = users.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    return users.create_user(db=db, user=user)

@app.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: User = Depends(get_current_user)
):
    return current_user

@app.get("/users/", response_model=List[User])
async def read_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "administrador":
        raise HTTPException(status_code=403, detail="No tiene permisos para ver todos los usuarios")
    return users.get_users(db, skip=skip, limit=limit)

# Endpoints para Departamentos
@app.get("/departments/", response_model=List[Department])
async def read_departments(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    return departments.get_departments(db, skip=skip, limit=limit)

@app.post("/departments/", response_model=Department)
async def create_department_endpoint(
    department: DepartmentCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "administrador":
        raise HTTPException(status_code=403, detail="No tiene permisos para crear departamentos")
    
    db_department = departments.get_department_by_name(db, name=department.nombre)
    if db_department:
        raise HTTPException(status_code=400, detail="Ya existe un departamento con ese nombre")
    
    return departments.create_department(db=db, department=department)

# Endpoints para Tickets
@app.post("/tickets/", response_model=Ticket)
async def create_ticket_endpoint(
    ticket: TicketCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return tickets.create_ticket(db=db, ticket=ticket, user_id=current_user.id)

@app.get("/tickets/", response_model=List[Ticket])
async def read_tickets(
    skip: int = 0, 
    limit: int = 100, 
    status: Optional[str] = None,
    department: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return tickets.get_tickets(
        db, 
        skip=skip, 
        limit=limit, 
        status=status,
        department=department,
        user_id=current_user.id,
        role=current_user.role
    )

@app.get("/tickets/{ticket_id}", response_model=Ticket)
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
    elif current_user.role == "soporte" and db_ticket.departamento_id != current_user.departamento_id and db_ticket.assigned_to != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene permisos para ver este ticket")
    
    return db_ticket

@app.patch("/tickets/{ticket_id}", response_model=Ticket)
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

@app.post("/tickets/{ticket_id}/comments/", response_model=Comment)
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
    elif current_user.role == "soporte" and db_ticket.departamento_id != current_user.departamento_id and db_ticket.assigned_to != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene permisos para comentar en este ticket")
    
    return tickets.add_comment(db, ticket_id, comment, current_user.id)

# Endpoints para Categorías
@app.post("/categorias/", response_model=Categoria)
async def create_categoria_endpoint(
    categoria_data: CategoriaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verificar permisos (solo administradores pueden crear categorías)
    if current_user.role != "administrador":
        raise HTTPException(status_code=403, detail="No tiene permisos para crear categorías")
    
    # Verificar si ya existe una categoría con el mismo nombre
    db_categoria = categoria.get_categoria_by_nombre(db, nombre=categoria_data.nombre)
    if db_categoria:
        raise HTTPException(status_code=400, detail="Ya existe una categoría con ese nombre")
    
    return categoria.create_categoria(db=db, categoria=categoria_data)

@app.get("/categorias/", response_model=List[Categoria])
async def read_categorias(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    categorias = categoria.get_categorias(db, skip=skip, limit=limit)
    return categorias

@app.get("/categorias/{categoria_id}", response_model=Categoria)
async def read_categoria(
    categoria_id: str,
    db: Session = Depends(get_db)
):
    db_categoria = categoria.get_categoria(db, categoria_id=categoria_id)
    if db_categoria is None:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return db_categoria

@app.put("/categorias/{categoria_id}", response_model=Categoria)
async def update_categoria_endpoint(
    categoria_id: str,
    categoria_data: CategoriaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verificar permisos
    if current_user.role != "administrador":
        raise HTTPException(status_code=403, detail="No tiene permisos para actualizar categorías")
    
    db_categoria = categoria.get_categoria(db, categoria_id=categoria_id)
    if db_categoria is None:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    return categoria.update_categoria(db=db, categoria_id=categoria_id, nombre=categoria_data.nombre)

@app.delete("/categorias/{categoria_id}", response_model=Categoria)
async def delete_categoria_endpoint(
    categoria_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verificar permisos
    if current_user.role != "administrador":
        raise HTTPException(status_code=403, detail="No tiene permisos para eliminar categorías")
    
    db_categoria = categoria.get_categoria(db, categoria_id=categoria_id)
    if db_categoria is None:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    return categoria.delete_categoria(db=db, categoria_id=categoria_id)

# Endpoints para asignar categorías a departamentos
@app.post("/categorias/{categoria_id}/departamentos/{departamento_id}")
async def assign_categoria_to_departamento_endpoint(
    categoria_id: str,
    departamento_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verificar permisos
    if current_user.role != "administrador":
        raise HTTPException(status_code=403, detail="No tiene permisos para asignar categorías a departamentos")
    
    # Verificar que existan la categoría y el departamento
    db_categoria = categoria.get_categoria(db, categoria_id=categoria_id)
    if db_categoria is None:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    db_departamento = departments.get_department(db, department_id=departamento_id)
    if db_departamento is None:
        raise HTTPException(status_code=404, detail="Departamento no encontrado")
    
    result = categoria.assign_categoria_to_departamento(db, categoria_id, departamento_id)
    if result:
        return {"message": "Categoría asignada al departamento correctamente"}
    else:
        return {"message": "La categoría ya estaba asignada al departamento"}

@app.delete("/categorias/{categoria_id}/departamentos/{departamento_id}")
async def remove_categoria_from_departamento_endpoint(
    categoria_id: str,
    departamento_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verificar permisos
    if current_user.role != "administrador":
        raise HTTPException(status_code=403, detail="No tiene permisos para desasignar categorías de departamentos")
    
    result = categoria.remove_categoria_from_departamento(db, categoria_id, departamento_id)
    if result:
        return {"message": "Categoría desasignada del departamento correctamente"}
    else:
        return {"message": "La categoría no estaba asignada al departamento"}

# Endpoints para Mensajes
@app.post("/mensajes/", response_model=Mensaje)
async def create_mensaje_endpoint(
    mensaje_data: MensajeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Opcional: Verificar que el usuario solo pueda crear mensajes propios
    if current_user.role != "administrador" and mensaje_data.users_id != current_user.id:
        mensaje_data.users_id = current_user.id
    
    return mensaje.create_mensaje(db=db, mensaje=mensaje_data)

@app.get("/mensajes/", response_model=List[Mensaje])
async def read_mensajes(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Si se especifica un user_id y el usuario actual no es administrador,
    # solo permitir ver mensajes propios
    if user_id and current_user.role != "administrador" and user_id != current_user.id:
        user_id = current_user.id
    
    if user_id:
        mensajes = mensaje.get_mensajes_by_user(db, user_id=user_id, skip=skip, limit=limit)
    else:
        # Si el usuario no es administrador, solo mostrar sus mensajes
        if current_user.role != "administrador":
            mensajes = mensaje.get_mensajes_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
        else:
            mensajes = mensaje.get_mensajes(db, skip=skip, limit=limit)
    
    return mensajes

@app.get("/mensajes/{mensaje_id}", response_model=Mensaje)
async def read_mensaje(
    mensaje_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_mensaje = mensaje.get_mensaje(db, mensaje_id=mensaje_id)
    if db_mensaje is None:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")
    
    # Verificar permisos
    if current_user.role != "administrador" and db_mensaje.users_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene permisos para ver este mensaje")
    
    return db_mensaje

@app.put("/mensajes/{mensaje_id}", response_model=Mensaje)
async def update_mensaje_endpoint(
    mensaje_id: str,
    mensaje_text: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_mensaje = mensaje.get_mensaje(db, mensaje_id=mensaje_id)
    if db_mensaje is None:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")
    
    # Verificar permisos
    if current_user.role != "administrador" and db_mensaje.users_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene permisos para actualizar este mensaje")
    
    return mensaje.update_mensaje(db=db, mensaje_id=mensaje_id, mensaje_text=mensaje_text)

@app.delete("/mensajes/{mensaje_id}", response_model=Mensaje)
async def delete_mensaje_endpoint(
    mensaje_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_mensaje = mensaje.get_mensaje(db, mensaje_id=mensaje_id)
    if db_mensaje is None:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")
    
    # Verificar permisos
    if current_user.role != "administrador" and db_mensaje.users_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene permisos para eliminar este mensaje")
    
    return mensaje.delete_mensaje(db=db, mensaje_id=mensaje_id)

# Endpoints para Attachments (archivos adjuntos)
@app.post("/attachments/", response_model=Attachment)
async def create_attachment_endpoint(
    file: UploadFile = File(...),
    ticket_id: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verificar que el ticket existe
    db_ticket = tickets.get_ticket(db, ticket_id=ticket_id)
    if db_ticket is None:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    
    # Verificar permisos
    if current_user.role != "administrador" and db_ticket.requested_by != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene permisos para adjuntar archivos a este ticket")
    
    # Crear directorio para archivos si no existe
    upload_dir = Path("uploads") / ticket_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Guardar el archivo
    file_path = upload_dir / file.filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Obtener extensión del archivo
    file_extension = os.path.splitext(file.filename)[1].lstrip(".")
    
    # Crear registro en la base de datos
    attachment_data = AttachmentCreate(
        file_name=file.filename,
        file_path=str(file_path),
        file_extension=file_extension,
        ticket_id=ticket_id
    )
    
    return attachment.create_attachment(db=db, attachment=attachment_data)

@app.get("/attachments/ticket/{ticket_id}", response_model=List[Attachment])
async def read_attachments_by_ticket(
    ticket_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verificar que el ticket existe
    db_ticket = tickets.get_ticket(db, ticket_id=ticket_id)
    if db_ticket is None:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    
    # Verificar permisos
    if current_user.role == "usuario" and db_ticket.requested_by != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene permisos para ver los adjuntos de este ticket")
    
    return attachment.get_attachments_by_ticket(db, ticket_id=ticket_id)

@app.get("/attachments/{attachment_id}", response_model=Attachment)
async def read_attachment(
    attachment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_attachment = attachment.get_attachment(db, attachment_id=attachment_id)
    if db_attachment is None:
        raise HTTPException(status_code=404, detail="Archivo adjunto no encontrado")
    
    # Verificar permisos
    db_ticket = tickets.get_ticket(db, ticket_id=db_attachment.ticket_id)
    if current_user.role == "usuario" and db_ticket.requested_by != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene permisos para ver este archivo adjunto")
    
    return db_attachment

@app.delete("/attachments/{attachment_id}", response_model=Attachment)
async def delete_attachment_endpoint(
    attachment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_attachment = attachment.get_attachment(db, attachment_id=attachment_id)
    if db_attachment is None:
        raise HTTPException(status_code=404, detail="Archivo adjunto no encontrado")
    
    # Verificar permisos
    db_ticket = tickets.get_ticket(db, ticket_id=db_attachment.ticket_id)
    if current_user.role != "administrador" and db_ticket.requested_by != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene permisos para eliminar este archivo adjunto")
    
    # Eliminar el archivo físico
    try:
        os.remove(db_attachment.file_path)
    except OSError:
        # Si el archivo no existe, continuamos con la eliminación del registro
        pass
    
    return attachment.delete_attachment(db=db, attachment_id=attachment_id)

# Punto de entrada para ejecutar la aplicación
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
