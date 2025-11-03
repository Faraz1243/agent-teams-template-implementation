from sqlalchemy import (
    Column, Integer, BigInteger, String, Text, TIMESTAMP,
    ForeignKey, func, CheckConstraint, event
)
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# 1️⃣ Chat Thread Model
class ChatThread(Base):
    __tablename__ = "chat_threads"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, nullable=False)
    title = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    messages = relationship("ChatMessage", back_populates="thread", cascade="all, delete")

    def __repr__(self):
        return f"<ChatThread(id={self.id}, user_id={self.user_id}, title={self.title})>"


# 2️⃣ Chat Message Model
class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(UUID, primary_key=True, default= uuid.uuid4)
    thread_id = Column(UUID, ForeignKey("chat_threads.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID, nullable=True)
    sender_role = Column(String(20), CheckConstraint("sender_role IN ('user', 'assistant')"), default="user")
    message = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    thread = relationship("ChatThread", back_populates="messages")

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, thread_id={self.thread_id}, sender_role={self.sender_role})>"
