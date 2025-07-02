# backend/db/models.py

from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class Email(Base):
    __tablename__ = "emails"

    id = Column(String, primary_key=True, index=True)
    thread_id = Column(String)
    sender = Column(String)
    subject = Column(String)
    snippet = Column(String)
    category = Column(String, default="General")
    job_company = Column(String, nullable=True)
    job_status = Column(String, default="Applied") # e.g., Applied, Interview, Offer, Rejected

    # --- NEW AND CRUCIAL COLUMN ---
    # This will store the UTC timestamp of when the email was received.
    # It's indexed for fast lookups to find the latest email.
    received_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationship to attachments
    attachments = relationship("Attachment", back_populates="email")

class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    mime_type = Column(String)
    size = Column(Integer)
    email_id = Column(String, ForeignKey("emails.id"))

    # Relationship to email
    email = relationship("Email", back_populates="attachments")
