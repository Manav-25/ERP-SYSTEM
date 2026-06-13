from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal


class VendorCreate(BaseModel):
    company_name: str
    contact_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: str = "India"
    gst_number: Optional[str] = None
    payment_terms: Optional[str] = None
    lead_time_days: int = 7


class VendorOut(BaseModel):
    id: int
    vendor_code: str
    company_name: str
    contact_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    lead_time_days: int
    is_active: bool
    created_at: datetime
    model_config = {"from_attributes": True}


class POItemCreate(BaseModel):
    product_id: int
    ordered_qty: Decimal
    unit_price: Decimal
    tax_pct: Decimal = Decimal("0.00")


class POItemOut(BaseModel):
    id: int
    product_id: int
    ordered_qty: Decimal
    received_qty: Decimal
    unit_price: Decimal
    tax_pct: Decimal
    line_total: Decimal
    model_config = {"from_attributes": True}


class PurchaseOrderCreate(BaseModel):
    vendor_id: int
    order_date: date
    expected_receipt_date: Optional[date] = None
    notes: Optional[str] = None
    items: List[POItemCreate]


class PurchaseOrderOut(BaseModel):
    id: int
    order_number: str
    vendor_id: int
    vendor: Optional[VendorOut] = None
    order_date: date
    expected_receipt_date: Optional[date] = None
    status: str
    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    auto_generated: bool
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    items: List[POItemOut] = []
    model_config = {"from_attributes": True}


class GRItemCreate(BaseModel):
    purchase_order_item_id: int
    product_id: int
    received_qty: Decimal


class GoodsReceiptCreate(BaseModel):
    purchase_order_id: int
    receipt_date: date
    notes: Optional[str] = None
    items: List[GRItemCreate]


class GoodsReceiptOut(BaseModel):
    id: int
    receipt_number: str
    purchase_order_id: int
    receipt_date: date
    notes: Optional[str] = None
    created_at: datetime
    model_config = {"from_attributes": True}
