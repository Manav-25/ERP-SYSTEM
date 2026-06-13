from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, DECIMAL, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
import enum


class ProcurementStrategy(str, enum.Enum):
    MTS = "MTS"
    MTO = "MTO"


class ProcurementType(str, enum.Enum):
    purchase = "purchase"
    manufacturing = "manufacturing"


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    products = relationship("Product", back_populates="category")
    subcategories = relationship("Category")


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    product_code = Column(String(50), unique=True, nullable=False, index=True)
    product_name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    cost_price = Column(DECIMAL(15, 2), default=0.00)
    sales_price = Column(DECIMAL(15, 2), default=0.00)
    on_hand_qty = Column(DECIMAL(15, 3), default=0.000)
    reserved_qty = Column(DECIMAL(15, 3), default=0.000)
    reorder_point = Column(DECIMAL(15, 3), default=0.000)
    unit_of_measure = Column(String(20), default="PCS")
    procurement_strategy = Column(Enum("MTS", "MTO"), default="MTS")
    procurement_type = Column(Enum("purchase", "manufacturing"), default="purchase")
    image_path = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    category = relationship("Category", back_populates="products")
    creator = relationship("User", foreign_keys=[created_by])
    boms = relationship("BOM", back_populates="product")
    stock_ledger = relationship("StockLedger", back_populates="product")

    @property
    def free_qty(self):
        return float(self.on_hand_qty or 0) - float(self.reserved_qty or 0)

    @property
    def is_low_stock(self):
        return float(self.on_hand_qty or 0) <= float(self.reorder_point or 0)
