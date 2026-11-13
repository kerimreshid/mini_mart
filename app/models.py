from sqlalchemy.sql import func

from app.database import Base
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Numeric,
    DateTime,
    Boolean,
    ForeignKey
)
from sqlalchemy.sql import func



class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    stock_quantity = Column(Integer, default=0, nullable=False)
    is_active = Column(
    Boolean,
    default=True,
    nullable=False
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    image_url = Column(String(500), nullable=True)


class InventoryMovement(Base):
     __tablename__ = "inventory_movements"

     id = Column(Integer, primary_key=True, index=True)

     product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False,
        index=True
    )

     movement_type = Column(String(30), nullable=False)

     quantity_change = Column(Integer, nullable=False)

     previous_quantity = Column(Integer, nullable=False)

     new_quantity = Column(Integer, nullable=False)

     reason = Column(String(255), nullable=True)

     created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )