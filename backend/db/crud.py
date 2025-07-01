# backend/db/crud.py

from sqlalchemy.orm import Session
from . import models

def get_email_by_id(db: Session, email_id: str):
    """
    Queries the database to find an email by its unique ID.
    """
    return db.query(models.Email).filter(models.Email.id == email_id).first()

def create_email(db: Session, email: models.Email):
    """
    Adds a new email record to the database and commits the transaction.
    """
    db.add(email)
    db.commit()
    db.refresh(email)
    return email