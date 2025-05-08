from sqlalchemy.orm import Session
from models.models import Ticket as DBTicket
from schemas.schemas import TicketCreate
from db.database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_ticket(ticket: TicketCreate):
    db = SessionLocal()
    db_ticket = DBTicket(**ticket.dict())
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

def get_tickets():
    db = SessionLocal()
    return db.query(DBTicket).all()
