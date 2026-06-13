from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, DECIMAL, Enum, Text, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    order_date = Column(Date, nullable=False)
    expected_receipt_date = Column(Date)
    status = Column(Enum("draft","confirmed","partially_received","fully_received","cancelled"), default="draft")
    subtotal = Column(DECIMAL(15, 2), default=0.00)
    tax_amount = Column(DECIMAL(15, 2), default=0.00)
    total_amount = Column(DECIMAL(15, 2), default=0.00)
    notes = Column(Text)
    auto_generated = Column(Boolean, default=False)
    reference_so_id = Column(Integer, ForeignKey("sales_orders.id", ondelete="SET NULL"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    vendor = relationship("Vendor", back_populates="purchase_orders")
    creator = relationship("User", foreign_keys=[created_by])
    items = relationship("PurchaseOrderItem", back_populates="purchase_order", cascade="all, delete-orphan")
    receipts = relationship("GoodsReceipt", back_populates="purchase_order")


class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"
    id = Column(Integer, primary_key=True, index=True)
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    ordered_qty = Column(DECIMAL(15, 3), nullable=False)
    received_qty = Column(DECIMAL(15, 3), default=0.000)
    unit_price = Column(DECIMAL(15, 2), nullable=False)
    tax_pct = Column(DECIMAL(5, 2), default=0.00)
    line_total = Column(DECIMAL(15, 2), nullable=False)

    purchase_order = relationship("PurchaseOrder", back_populates="items")
    product = relationship("Product")


class GoodsReceipt(Base):
    __tablename__ = "goods_receipts"
    id = Column(Integer, primary_key=True, index=True)
    receipt_number = Column(String(50), unique=True, nullable=False)
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False)
    receipt_date = Column(Date, nullable=False)
    notes = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    purchase_order = relationship("PurchaseOrder", back_populates="receipts")
    items = relationship("GoodsReceiptItem", back_populates="receipt", cascade="all, delete-orphan")
    creator = relationship("User", foreign_keys=[created_by])


class GoodsReceiptItem(Base):
    __tablename__ = "goods_receipt_items"
    id = Column(Integer, primary_key=True, index=True)
    receipt_id = Column(Integer, ForeignKey("goods_receipts.id", ondelete="CASCADE"), nullable=False)
    purchase_order_item_id = Column(Integer, ForeignKey("purchase_order_items.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    received_qty = Column(DECIMAL(15, 3), nullable=False)

    receipt = relationship("GoodsReceipt", back_populates="items")
    product = relationship("Product")
