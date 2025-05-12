from sqlalchemy.orm import Session
from models.database_models import Attachment
from models.schemas import AttachmentCreate

def get_attachment(db: Session, attachment_id: str):
    return db.query(Attachment).filter(Attachment.id == attachment_id).first()

def get_attachments_by_ticket(db: Session, ticket_id: str):
    return db.query(Attachment).filter(Attachment.ticket_id == ticket_id).all()

def create_attachment(db: Session, attachment: AttachmentCreate):
    db_attachment = Attachment(
        file_name=attachment.file_name,
        file_path=attachment.file_path,
        file_extension=attachment.file_extension,
        ticket_id=attachment.ticket_id
    )
    db.add(db_attachment)
    db.commit()
    db.refresh(db_attachment)
    return db_attachment

def delete_attachment(db: Session, attachment_id: str):
    db_attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()
    if db_attachment:
        db.delete(db_attachment)
        db.commit()
    return db_attachment
