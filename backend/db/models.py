# backend/db/models.py
from sqlalchemy import Column, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Email(Base):
    __tablename__ = "emails"

    id = Column(String, primary_key=True, index=True) # This is the Gmail message ID
    thread_id = Column(String, index=True)
    sender = Column(String)
    subject = Column(String)
    snippet = Column(Text)
    # We will add more fields like date later