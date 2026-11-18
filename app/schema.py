from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class ProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str | None = None
    category: str
    price: float = Field(gt=0)
    stock_quantity: int = Field(ge=0)



class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None
    category: str
    price: float
    stock_quantity: int
    created_at: datetime | None = None
    is_active: bool
    image_url: str | None = None
    model_config = ConfigDict(from_attributes=True)



class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = None
    category: str | None = Field(default=None, min_length=2, max_length=100)
    price: float | None = Field(default=None, gt=0)
    stock_quantity: int | None = Field(default=None, ge=0)
    is_active: bool | None = None
    image_url: str | None = None



class StockRestock(BaseModel):
    quantity: int = Field(gt=0)
    reason: str = Field(min_length=3, max_length=255)



class StockCorrection(BaseModel):
    actual_quantity: int = Field(ge=0)
    reason: str = Field(min_length=3, max_length=255)



class StockMovementResponse(BaseModel):
    id: int
    product_id: int
    movement_type: str
    quantity_change: int
    previous_quantity: int
    new_quantity: int
    reason: str | None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class SaleItemCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


class SaleCreate(BaseModel):
    customer_id: int | None = None

    items: list[SaleItemCreate] = Field(
        min_length=1,
        max_length=50
    )


class SaleItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: float
    subtotal: float

    model_config = ConfigDict(from_attributes=True)


class SaleResponse(BaseModel):
    id: int
    total_amount: float
    created_at: datetime
    items: list[SaleItemResponse]
    customer_id: int | None
    
    model_config = ConfigDict(from_attributes=True)


 
class CustomerCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=60)
    phone: Optional[str] = Field(default=None, max_length=30)
    email: Optional[str] = Field(default=None, max_length=50)
    

class CustomerUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=60)
    phone: Optional[str] = Field(default=None, max_length=30)
    email: Optional[str] = Field(default=None, max_length=50)



class CustomerStatusUpdate(BaseModel):
    is_active: bool



class CustomerResponse(BaseModel):
    id: int
    full_name: str
    phone: Optional[str]
    email: Optional[str]
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

