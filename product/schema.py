from pydantic import BaseModel, field_validator
from typing import Optional
from decimal import Decimal
from datetime import datetime


class ProductCreateSchema(BaseModel):
    title: str
    desc: Optional[str] = None
    price: Decimal

    model_config = {
        "from_attributes": True
    }

    @field_validator('title')
    @classmethod
    def check_title(cls, value):
        if value.isdigit():
            raise ValueError(
                "Product nomi raqamlardan tashkil topmasin"
            )
        return value

    @field_validator('price')
    @classmethod
    def check_price(cls, value):
        if value < 0:
            raise ValueError(
                "Narx manfiy bo'lmasligi kerak"
            )
        return value


class ProductOutSchema(ProductCreateSchema):
    id: int
    created_at: datetime
    is_active:bool
    
    
class ProductUpdateSchema(ProductCreateSchema):
    title: Optional[str] = None
    price: Optional[Decimal] = None

    model_config = {
        "from_attributes": True
    }