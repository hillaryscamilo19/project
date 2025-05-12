from sqlalchemy.orm import Session
from models.database_models import Comment
from models.schemas import CommentCreate

def get_comment(db: Session, comment_id: str):
    return db.query(Comment).filter(Comment.id == comment_id).first()

def get_comments_by_ticket(db: Session, ticket_id: str):
    return db.query(Comment).filter(Comment.ticket_id == ticket_id).all()

def create_comment(db: Session, comment: CommentCreate):
    db_comment = Comment(
        content=comment.content,
        ticket_id=comment.ticket_id,
        user_id=comment.user_id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

def delete_comment(db: Session, comment_id: str):
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if db_comment:
        db.delete(db_comment)
        db.commit()
    return db_comment
