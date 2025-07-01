# backend/db/models.py
from sqlalchemy import Column, String, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Email(Base):
    __tablename__ = "emails"

    id = Column(String, primary_key=True, index=True) # This is the Gmail message ID
    thread_id = Column(String, index=True)
    sender = Column(String)
    subject = Column(String)
    snippet = Column(Text)

    # This creates the one-to-many relationship
    attachments = relationship("Attachment", back_populates="email")

class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    mime_type = Column(String)
    size = Column(Integer)

    # Foreign key to link back to the Email table
    email_id = Column(String, ForeignKey("emails.id"))

    # This creates the many-to-one relationship
    email = relationship("Email", back_populates="attachments")