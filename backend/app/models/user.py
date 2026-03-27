from sqlalchemy import Column, Integer, String
from app.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(200), unique=True)
    password_hash = Column(String(200), nullable=False)
    role = Column(String(20), default="user")  # user / admin / readonly
    department = Column(String(100))
