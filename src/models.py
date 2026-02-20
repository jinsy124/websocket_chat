from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from src.database import Base

# 👤 User
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)


# 💬 Conversation
class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True)
    user1 = Column(Integer, ForeignKey("users.id"))
    user2 = Column(Integer, ForeignKey("users.id"))
    last_message = Column(String, nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


# 📨 Message
class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    sender_id = Column(Integer, ForeignKey("users.id"))
    text = Column(String)
    created_at = Column(DateTime, server_default=func.now())