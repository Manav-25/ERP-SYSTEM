from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, DECIMAL, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class BOM(Base):
    __tablename__ = "boms"
    id = Column(Integer, primary_key=True, index=True)
    bom_code = Column(String(50), unique=True, nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    version = Column(String(20), default="1.0")
    quantity = Column(DECIMAL(15, 3), default=1.000)
    is_active = Column(Boolean, default=True)
    notes = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    product = relationship("Product", back_populates="boms")
    components = relationship("BOMComponent", back_populates="bom", cascade="all, delete-orphan")
    operations = relationship("Operation", back_populates="bom", cascade="all, delete-orphan")
    manufacturing_orders = relationship("ManufacturingOrder", back_populates="bom")
    creator = relationship("User", foreign_keys=[created_by])


class BOMComponent(Base):
    __tablename__ = "bom_components"
    id = Column(Integer, primary_key=True, index=True)
    bom_id = Column(Integer, ForeignKey("boms.id", ondelete="CASCADE"), nullable=False)
    component_product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(DECIMAL(15, 3), nullable=False)
    unit_of_measure = Column(String(20), default="PCS")
    notes = Column(Text)

    bom = relationship("BOM", back_populates="components")
    component = relationship("Product")


class WorkCenter(Base):
    __tablename__ = "work_centers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    capacity_per_hour = Column(DECIMAL(10, 2), default=1.00)
    cost_per_hour = Column(DECIMAL(10, 2), default=0.00)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    operations = relationship("Operation", back_populates="work_center")
    work_orders = relationship("WorkOrder", back_populates="work_center")


class Operation(Base):
    __tablename__ = "operations"
    id = Column(Integer, primary_key=True, index=True)
    bom_id = Column(Integer, ForeignKey("boms.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    work_center_id = Column(Integer, ForeignKey("work_centers.id", ondelete="SET NULL"), nullable=True)
    sequence = Column(Integer, default=1)
    duration_hours = Column(DECIMAL(8, 2), default=0.00)
    description = Column(Text)

    bom = relationship("BOM", back_populates="operations")
    work_center = relationship("WorkCenter", back_populates="operations")
