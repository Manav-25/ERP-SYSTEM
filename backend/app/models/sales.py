from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, DECIMAL, Enum, Text, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class SalesOrder(Base):
    __tablename__ = "sales_orders"
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    order_date = Column(Date, nullable=False)
    expected_delivery_date = Column(Date)
    status = Column(Enum("draft","confirmed","partially_delivered","fully_delivered","cancelled"), default="draft")
    subtotal = Column(DECIMAL(15, 2), default=0.00)
    tax_amount = Column(DECIMAL(15, 2), default=0.00)
    discount_amount = Column(DECIMAL(15, 2), default=0.00)
    total_amount = Column(DECIMAL(15, 2), default=0.00)
    notes = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    confirmed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    customer = relationship("Customer", back_populates="sales_orders")
    creator = relationship("User", foreign_keys=[created_by])
    confirmer = relationship("User", foreign_keys=[confirmed_by])
    items = relationship("SalesOrderItem", back_populates="sales_order", cascade="all, delete-orphan")
    deliveries = relationship("Delivery", back_populates="sales_order")


class SalesOrderItem(Base):
    __tablename__ = "sales_order_items"
    id = Column(Integer, primary_key=True, index=True)
    sales_order_id = Column(Integer, ForeignKey("sales_orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    ordered_qty = Column(DECIMAL(15, 3), nullable=False)
    delivered_qty = Column(DECIMAL(15, 3), default=0.000)
    unit_price = Column(DECIMAL(15, 2), nullable=False)
    discount_pct = Column(DECIMAL(5, 2), default=0.00)
    tax_pct = Column(DECIMAL(5, 2), default=0.00)
    line_total = Column(DECIMAL(15, 2), nullable=False)

    sales_order = relationship("SalesOrder", back_populates="items")
    product = relationship("Product")


class Delivery(Base):
    __tablename__ = "deliveries"
    id = Column(Integer, primary_key=True, index=True)
    delivery_number = Column(String(50), unique=True, nullable=False)
    sales_order_id = Column(Integer, ForeignKey("sales_orders.id"), nullable=False)
    delivery_date = Column(Date, nullable=False)
    status = Column(Enum("pending","in_transit","delivered","cancelled"), default="pending")
    notes = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sales_order = relationship("SalesOrder", back_populates="deliveries")
    items = relationship("DeliveryItem", back_populates="delivery", cascade="all, delete-orphan")
    creator = relationship("User", foreign_keys=[created_by])


class DeliveryItem(Base):
    __tablename__ = "delivery_items"
    id = Column(Integer, primary_key=True, index=True)
    delivery_id = Column(Integer, ForeignKey("deliveries.id", ondelete="CASCADE"), nullable=False)
    sales_order_item_id = Column(Integer, ForeignKey("sales_order_items.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    delivered_qty = Column(DECIMAL(15, 3), nullable=False)

    delivery = relationship("Delivery", back_populates="items")
    product = relationship("Product")
