from sqlalchemy import Column, Integer, String, Boolean, DateTime, DECIMAL, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    customer_code = Column(String(50), unique=True, nullable=False, index=True)
    company_name = Column(String(255), nullable=False, index=True)
    contact_name = Column(String(255))
    email = Column(String(255))
    phone = Column(String(30))
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100), default="India")
    gst_number = Column(String(20))
    credit_limit = Column(DECIMAL(15, 2), default=0.00)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    sales_orders = relationship("SalesOrder", back_populates="customer")
