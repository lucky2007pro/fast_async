from sqlalchemy import Column, String, Numeric, Boolean, Integer, DateTime
from db import Base
from datetime import datetime


class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(50), nullable=False)
    desc = Column(String)
    price = Column(Numeric(10, 2), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    
    


