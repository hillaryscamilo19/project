from sqlalchemy.orm import Session
from models.database_models import Ticket, Comment
from models.schemas import TicketCreate, TicketUpdate, CommentCreate
from datetime import datetime

def get_ticket(db: Session, ticket_id: str):
    return db.query(Ticket).filter(Ticket.id == ticket_id).first()

def get_tickets(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    status: str = None,
    departamento: str = None,
    user_id: str = None,
    role: str = None
):
    query = db.query(Ticket)
    
    if status:
        query = query.filter(Ticket.status == status)
    
    if departamento:
        query = query.filter(Ticket.departamento == departamento)
    
    # Filtrar por rol y usuario
    if role == "usuario":
        query = query.filter(Ticket.requested_by == user_id)
    elif role == "soporte":
        query = query.filter(
            (Ticket.departamento == departamento) | (Ticket.assigned_to == user_id)
        )
    
    return query.offset(skip).limit(limit).all()

def create_ticket(db: Session, ticket: TicketCreate, user_id: str):
    db_ticket = Ticket(
        title=ticket.title,
        description=ticket.description,
        departamento=ticket.departamento,
        priority=ticket.priority,
        status="abierto",
        requested_by=user_id
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

def update_ticket(db: Session, ticket_id: str, ticket_update: TicketUpdate):
    db_ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    
    if not db_ticket:
        return None
    
    update_data = ticket_update.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_ticket, key, value)
    
    db_ticket.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

def add_comment(db: Session, ticket_id: str, comment: CommentCreate, user_id: str):
    db_comment = Comment(
        content=comment.content,
        ticket_id=ticket_id,
        user_id=user_id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment