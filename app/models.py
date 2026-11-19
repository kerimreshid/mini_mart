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
from sqlalchemy.orm import relationship


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



class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)

    total_amount = Column(
        Numeric(12, 2),
        nullable=False,
        default=0
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    items = relationship(
        "SaleItem",
        back_populates="sale",
        cascade="all, delete-orphan"
    )
    customer_id = Column(
    Integer,
    ForeignKey("customers.id"),
    nullable=True,
    index=True
   )

    customer = relationship("Customer", back_populates="sales")



class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True, index=True)

    sale_id = Column(
        Integer,
        ForeignKey("sales.id"),
        nullable=False,
        index=True
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False,
        index=True
    )

    quantity = Column(Integer, nullable=False)

    unit_price = Column(Numeric(10, 2), nullable=False)

    subtotal = Column(Numeric(12, 2), nullable=False)

    sale = relationship(
        "Sale",
        back_populates="items"

    )



class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)
    phone = Column(String(30), nullable=True)
    email = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    sales = relationship("Sale", back_populates="customer")


class User(Base):
    __tablename__ = "staff_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="cashier")
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )


