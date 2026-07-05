from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func

from db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    
    
class Blacklist(Base):
    __tablename__ = "blacklist"
    
    id = Column(Integer, primary_key=True)
    refresh = Column(String(255), unique=True, nullable=False)
    exp_time = Column(DateTime, default=func.now())