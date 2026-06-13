from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal


class CustomerCreate(BaseModel):
    company_name: str
    contact_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: str = "India"
    gst_number: Optional[str] = None
    credit_limit: Decimal = Decimal("0.00")


class CustomerUpdate(CustomerCreate):
    company_name: Optional[str] = None
    is_active: Optional[bool] = None


class CustomerOut(BaseModel):
    id: int
    customer_code: str
    company_name: str
    contact_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    gst_number: Optional[str] = None
    credit_limit: Decimal
    is_active: bool
    created_at: datetime
    model_config = {"from_attributes": True}


class SOItemCreate(BaseModel):
    product_id: int
    ordered_qty: Decimal
    unit_price: Decimal
    discount_pct: Decimal = Decimal("0.00")
    tax_pct: Decimal = Decimal("0.00")


class SOItemOut(BaseModel):
    id: int
    product_id: int
    ordered_qty: Decimal
    delivered_qty: Decimal
    unit_price: Decimal
    discount_pct: Decimal
    tax_pct: Decimal
    line_total: Decimal
    model_config = {"from_attributes": True}


class SalesOrderCreate(BaseModel):
    customer_id: int
    order_date: date
    expected_delivery_date: Optional[date] = None
    notes: Optional[str] = None
    items: List[SOItemCreate]


class SalesOrderUpdate(BaseModel):
    expected_delivery_date: Optional[date] = None
    notes: Optional[str] = None


class SalesOrderOut(BaseModel):
    id: int
    order_number: str
    customer_id: int
    customer: Optional[CustomerOut] = None
    order_date: date
    expected_delivery_date: Optional[date] = None
    status: str
    subtotal: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    items: List[SOItemOut] = []
    model_config = {"from_attributes": True}


class DeliveryItemCreate(BaseModel):
    sales_order_item_id: int
    product_id: int
    delivered_qty: Decimal


class DeliveryCreate(BaseModel):
    sales_order_id: int
    delivery_date: date
    notes: Optional[str] = None
    items: List[DeliveryItemCreate]


class DeliveryOut(BaseModel):
    id: int
    delivery_number: str
    sales_order_id: int
    delivery_date: date
    status: str
    notes: Optional[str] = None
    created_at: datetime
    model_config = {"from_attributes": True}
