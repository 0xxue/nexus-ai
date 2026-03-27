from sqlalchemy import Column, Integer, String, ForeignKey, Text
from app.models.base import Base, TimestampMixin


class Feedback(Base, TimestampMixin):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer)  # 1=thumbs up, -1=thumbs down
    comment = Column(Text)


class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(50), nullable=False)  # qa_ask / kb_upload / login
    query = Column(Text)
    answer_preview = Column(String(500))
    model_used = Column(String(50))
    tokens_consumed = Column(Integer, default=0)
    confidence = Column(Integer)
    ip_address = Column(String(50))
