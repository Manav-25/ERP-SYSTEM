from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal


class WorkCenterCreate(BaseModel):
    name: str
    description: Optional[str] = None
    capacity_per_hour: Decimal = Decimal("1.00")
    cost_per_hour: Decimal = Decimal("0.00")


class WorkCenterOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    capacity_per_hour: Decimal
    cost_per_hour: Decimal
    is_active: bool
    model_config = {"from_attributes": True}


class BOMComponentCreate(BaseModel):
    component_product_id: int
    quantity: Decimal
    unit_of_measure: str = "PCS"
    notes: Optional[str] = None


class OperationCreate(BaseModel):
    name: str
    work_center_id: Optional[int] = None
    sequence: int = 1
    duration_hours: Decimal = Decimal("0.00")
    description: Optional[str] = None


class BOMCreate(BaseModel):
    product_id: int
    version: str = "1.0"
    quantity: Decimal = Decimal("1.000")
    notes: Optional[str] = None
    components: List[BOMComponentCreate] = []
    operations: List[OperationCreate] = []


class BOMComponentOut(BaseModel):
    id: int
    component_product_id: int
    quantity: Decimal
    unit_of_measure: str
    notes: Optional[str] = None
    model_config = {"from_attributes": True}


class OperationOut(BaseModel):
    id: int
    name: str
    work_center_id: Optional[int] = None
    sequence: int
    duration_hours: Decimal
    description: Optional[str] = None
    model_config = {"from_attributes": True}


class BOMOut(BaseModel):
    id: int
    bom_code: str
    product_id: int
    version: str
    quantity: Decimal
    is_active: bool
    notes: Optional[str] = None
    created_at: datetime
    components: List[BOMComponentOut] = []
    operations: List[OperationOut] = []
    model_config = {"from_attributes": True}


class MOCreate(BaseModel):
    product_id: int
    bom_id: Optional[int] = None
    planned_qty: Decimal
    scheduled_start: Optional[date] = None
    scheduled_end: Optional[date] = None
    notes: Optional[str] = None


class MOOut(BaseModel):
    id: int
    mo_number: str
    product_id: int
    bom_id: Optional[int] = None
    planned_qty: Decimal
    produced_qty: Decimal
    scheduled_start: Optional[date] = None
    scheduled_end: Optional[date] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    status: str
    auto_generated: bool
    notes: Optional[str] = None
    created_at: datetime
    model_config = {"from_attributes": True}


class WorkOrderOut(BaseModel):
    id: int
    wo_number: str
    manufacturing_order_id: int
    planned_duration_hours: Decimal
    actual_duration_hours: Decimal
    status: str
    notes: Optional[str] = None
    model_config = {"from_attributes": True}
