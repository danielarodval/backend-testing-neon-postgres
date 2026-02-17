from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.database import Base

class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, nullable=False)
    delivery_id = Column(String, unique=True, index=True)
    signature = Column(String)
    payload = Column(JSON)
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<WebhookEvent(id={self.id}, event_type='{self.event_type}')>"