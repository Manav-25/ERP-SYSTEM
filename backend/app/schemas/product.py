from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None


class CategoryOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None
    created_at: datetime
    model_config = {"from_attributes": True}


class ProductCreate(BaseModel):
    product_code: str
    product_name: str
    description: Optional[str] = None
    category_id: Optional[int] = None
    cost_price: Decimal = Decimal("0.00")
    sales_price: Decimal = Decimal("0.00")
    reorder_point: Decimal = Decimal("0.000")
    unit_of_measure: str = "PCS"
    procurement_strategy: str = "MTS"
    procurement_type: str = "purchase"

    @field_validator("procurement_strategy")
    @classmethod
    def validate_strategy(cls, v):
        if v not in ("MTS", "MTO"):
            raise ValueError("procurement_strategy must be MTS or MTO")
        return v

    @field_validator("procurement_type")
    @classmethod
    def validate_type(cls, v):
        if v not in ("purchase", "manufacturing"):
            raise ValueError("procurement_type must be purchase or manufacturing")
        return v


class ProductUpdate(BaseModel):
    product_name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    cost_price: Optional[Decimal] = None
    sales_price: Optional[Decimal] = None
    reorder_point: Optional[Decimal] = None
    unit_of_measure: Optional[str] = None
    procurement_strategy: Optional[str] = None
    procurement_type: Optional[str] = None
    is_active: Optional[bool] = None


class ProductOut(BaseModel):
    id: int
    product_code: str
    product_name: str
    description: Optional[str] = None
    category_id: Optional[int] = None
    category: Optional[CategoryOut] = None
    cost_price: Decimal
    sales_price: Decimal
    on_hand_qty: Decimal
    reserved_qty: Decimal
    free_qty: float
    reorder_point: Decimal
    unit_of_measure: str
    procurement_strategy: str
    procurement_type: str
    image_path: Optional[str] = None
    is_active: bool
    is_low_stock: bool
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class StockAdjustment(BaseModel):
    product_id: int
    quantity: Decimal
    notes: Optional[str] = None
