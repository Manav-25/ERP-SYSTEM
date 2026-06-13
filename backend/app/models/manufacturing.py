from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, DECIMAL, Enum, Text, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class ManufacturingOrder(Base):
    __tablename__ = "manufacturing_orders"
    id = Column(Integer, primary_key=True, index=True)
    mo_number = Column(String(50), unique=True, nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    bom_id = Column(Integer, ForeignKey("boms.id", ondelete="SET NULL"), nullable=True)
    planned_qty = Column(DECIMAL(15, 3), nullable=False)
    produced_qty = Column(DECIMAL(15, 3), default=0.000)
    scheduled_start = Column(Date)
    scheduled_end = Column(Date)
    actual_start = Column(DateTime(timezone=True), nullable=True)
    actual_end = Column(DateTime(timezone=True), nullable=True)
    status = Column(Enum("draft","confirmed","in_progress","completed","cancelled"), default="draft")
    auto_generated = Column(Boolean, default=False)
    reference_so_id = Column(Integer, ForeignKey("sales_orders.id", ondelete="SET NULL"), nullable=True)
    notes = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    product = relationship("Product")
    bom = relationship("BOM", back_populates="manufacturing_orders")
    creator = relationship("User", foreign_keys=[created_by])
    work_orders = relationship("WorkOrder", back_populates="manufacturing_order", cascade="all, delete-orphan")
    components = relationship("MOComponent", back_populates="manufacturing_order", cascade="all, delete-orphan")


class WorkOrder(Base):
    __tablename__ = "work_orders"
    id = Column(Integer, primary_key=True, index=True)
    wo_number = Column(String(50), unique=True, nullable=False, index=True)
    manufacturing_order_id = Column(Integer, ForeignKey("manufacturing_orders.id", ondelete="CASCADE"), nullable=False)
    operation_id = Column(Integer, ForeignKey("operations.id", ondelete="SET NULL"), nullable=True)
    work_center_id = Column(Integer, ForeignKey("work_centers.id", ondelete="SET NULL"), nullable=True)
    planned_duration_hours = Column(DECIMAL(8, 2), default=0.00)
    actual_duration_hours = Column(DECIMAL(8, 2), default=0.00)
    status = Column(Enum("pending","in_progress","completed","cancelled"), default="pending")
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    manufacturing_order = relationship("ManufacturingOrder", back_populates="work_orders")
    operation = relationship("Operation")
    work_center = relationship("WorkCenter", back_populates="work_orders")


class MOComponent(Base):
    __tablename__ = "mo_components"
    id = Column(Integer, primary_key=True, index=True)
    manufacturing_order_id = Column(Integer, ForeignKey("manufacturing_orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    required_qty = Column(DECIMAL(15, 3), nullable=False)
    consumed_qty = Column(DECIMAL(15, 3), default=0.000)

    manufacturing_order = relationship("ManufacturingOrder", back_populates="components")
    product = relationship("Product")
