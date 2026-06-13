from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, DECIMAL, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class StockLedger(Base):
    __tablename__ = "stock_ledger"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    movement_date = Column(DateTime(timezone=True), server_default=func.now())
    movement_type = Column(Enum(
        "purchase_receipt","sales_delivery","manufacturing_consumption",
        "manufacturing_production","manual_adjustment","opening_stock",
        "return_from_customer","return_to_vendor"
    ), nullable=False)
    quantity = Column(DECIMAL(15, 3), nullable=False)
    balance_qty = Column(DECIMAL(15, 3), nullable=False)
    unit_cost = Column(DECIMAL(15, 4), default=0.0000)
    reference_type = Column(String(50))
    reference_id = Column(Integer)
    reference_number = Column(String(100))
    notes = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="stock_ledger")
    creator = relationship("User", foreign_keys=[created_by])


class StockReservation(Base):
    __tablename__ = "stock_reservations"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    reserved_qty = Column(DECIMAL(15, 3), nullable=False)
    reservation_type = Column(Enum("sales_order", "manufacturing_order"), nullable=False)
    reference_id = Column(Integer, nullable=False)
    reference_number = Column(String(100))
    is_released = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    released_at = Column(DateTime(timezone=True), nullable=True)

    product = relationship("Product")
