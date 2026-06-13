from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, date
from ..database import get_db
from ..models.manufacturing import ManufacturingOrder, WorkOrder, MOComponent
from ..models.bom import BOM, WorkCenter
from ..models.product import Product
from ..models.user import User
from ..schemas.manufacturing import (
    BOMCreate, BOMOut, WorkCenterCreate, WorkCenterOut,
    MOCreate, MOOut, WorkOrderOut,
)
from ..utils.helpers import paginate, get_next_sequence
from ..middleware.auth_middleware import get_current_user, require_permission
from ..services.inventory_service import record_stock_movement

router = APIRouter(prefix="/manufacturing", tags=["Manufacturing"])


# ── Work Centers ───────────────────────────────────────────────────────────────

@router.get("/work-centers", response_model=List[WorkCenterOut])
def list_work_centers(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(WorkCenter).filter(WorkCenter.is_active == True).all()


@router.post("/work-centers", response_model=WorkCenterOut, status_code=201)
def create_work_center(
    data: WorkCenterCreate, db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manufacturing", "create")),
):
    wc = WorkCenter(**data.model_dump())
    db.add(wc)
    db.commit()
    db.refresh(wc)
    return wc


# ── BOMs ───────────────────────────────────────────────────────────────────────

@router.get("/boms", response_model=dict)
def list_boms(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    product_id: Optional[int] = None,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    q = db.query(BOM).filter(BOM.is_active == True)
    if product_id:
        q = q.filter(BOM.product_id == product_id)
    result = paginate(q.order_by(BOM.created_at.desc()), page, page_size)
    result["items"] = [BOMOut.model_validate(b) for b in result["items"]]
    return result


@router.post("/boms", response_model=BOMOut, status_code=201)
def create_bom(
    data: BOMCreate, db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("bom", "create")),
):
    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")

    bom_code = get_next_sequence(db, "BOM")
    from ..models.bom import BOMComponent, Operation
    bom = BOM(
        bom_code=bom_code,
        product_id=data.product_id,
        version=data.version,
        quantity=data.quantity,
        notes=data.notes,
        created_by=current_user.id,
    )
    db.add(bom)
    db.flush()

    for comp in data.components:
        db.add(BOMComponent(bom_id=bom.id, **comp.model_dump()))
    for op in data.operations:
        db.add(Operation(bom_id=bom.id, **op.model_dump()))

    db.commit()
    db.refresh(bom)
    return BOMOut.model_validate(bom)


@router.get("/boms/{bom_id}", response_model=BOMOut)
def get_bom(bom_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    bom = db.query(BOM).filter(BOM.id == bom_id).first()
    if not bom:
        raise HTTPException(404, "BOM not found")
    return BOMOut.model_validate(bom)


# ── Manufacturing Orders ───────────────────────────────────────────────────────

@router.get("/orders", response_model=dict)
def list_orders(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None, product_id: Optional[int] = None,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    q = db.query(ManufacturingOrder)
    if status:
        q = q.filter(ManufacturingOrder.status == status)
    if product_id:
        q = q.filter(ManufacturingOrder.product_id == product_id)
    result = paginate(q.order_by(ManufacturingOrder.created_at.desc()), page, page_size)
    result["items"] = [MOOut.model_validate(o) for o in result["items"]]
    return result


@router.post("/orders", response_model=MOOut, status_code=201)
def create_order(
    data: MOCreate, db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manufacturing", "create")),
):
    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")

    bom = None
    if data.bom_id:
        bom = db.query(BOM).filter(BOM.id == data.bom_id).first()
    elif product.procurement_type == "manufacturing":
        bom = db.query(BOM).filter(BOM.product_id == product.id, BOM.is_active == True).first()

    mo_number = get_next_sequence(db, "MO")
    mo = ManufacturingOrder(
        mo_number=mo_number,
        product_id=data.product_id,
        bom_id=bom.id if bom else None,
        planned_qty=data.planned_qty,
        scheduled_start=data.scheduled_start,
        scheduled_end=data.scheduled_end,
        notes=data.notes,
        created_by=current_user.id,
    )
    db.add(mo)
    db.flush()

    if bom:
        for comp in bom.components:
            needed = float(comp.quantity) * float(data.planned_qty)
            db.add(MOComponent(
                manufacturing_order_id=mo.id,
                product_id=comp.component_product_id,
                required_qty=needed,
            ))

        wo_number = get_next_sequence(db, "WO")
        for op in sorted(bom.operations, key=lambda x: x.sequence):
            wo_num = get_next_sequence(db, "WO")
            db.add(WorkOrder(
                wo_number=wo_num,
                manufacturing_order_id=mo.id,
                operation_id=op.id,
                work_center_id=op.work_center_id,
                planned_duration_hours=op.duration_hours,
            ))

    db.commit()
    db.refresh(mo)
    return MOOut.model_validate(mo)


@router.get("/orders/{mo_id}", response_model=MOOut)
def get_order(mo_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    mo = db.query(ManufacturingOrder).filter(ManufacturingOrder.id == mo_id).first()
    if not mo:
        raise HTTPException(404, "Manufacturing order not found")
    return MOOut.model_validate(mo)


@router.post("/orders/{mo_id}/confirm")
def confirm_order(
    mo_id: int, db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manufacturing", "update")),
):
    mo = db.query(ManufacturingOrder).filter(ManufacturingOrder.id == mo_id).first()
    if not mo or mo.status != "draft":
        raise HTTPException(400, "Cannot confirm")
    mo.status = "confirmed"
    db.commit()
    return {"message": "Manufacturing order confirmed"}


@router.post("/orders/{mo_id}/start")
def start_order(
    mo_id: int, db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manufacturing", "update")),
):
    mo = db.query(ManufacturingOrder).filter(ManufacturingOrder.id == mo_id).first()
    if not mo or mo.status != "confirmed":
        raise HTTPException(400, "Order must be confirmed to start")

    for comp in mo.components:
        product = db.query(Product).filter(Product.id == comp.product_id).first()
        if product and float(product.on_hand_qty) < float(comp.required_qty):
            raise HTTPException(
                400,
                f"Insufficient stock for {product.product_name}: "
                f"need {comp.required_qty}, have {product.on_hand_qty}"
            )

    for comp in mo.components:
        product = db.query(Product).filter(Product.id == comp.product_id).first()
        record_stock_movement(
            db=db, product=product,
            quantity=-float(comp.required_qty),
            movement_type="manufacturing_consumption",
            reference_type="manufacturing_order",
            reference_id=mo.id,
            reference_number=mo.mo_number,
            notes=f"Component consumption for MO {mo.mo_number}",
            user_id=current_user.id,
        )
        comp.consumed_qty = comp.required_qty

    mo.status = "in_progress"
    mo.actual_start = datetime.utcnow()
    for wo in mo.work_orders:
        if wo.status == "pending":
            wo.status = "in_progress"
            wo.started_at = datetime.utcnow()
            break

    db.commit()
    return {"message": "Manufacturing order started, components consumed"}


@router.post("/orders/{mo_id}/complete")
def complete_order(
    mo_id: int, produced_qty: float = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manufacturing", "update")),
):
    mo = db.query(ManufacturingOrder).filter(ManufacturingOrder.id == mo_id).first()
    if not mo or mo.status != "in_progress":
        raise HTTPException(400, "Order must be in progress to complete")

    qty = produced_qty or float(mo.planned_qty)
    product = db.query(Product).filter(Product.id == mo.product_id).first()

    record_stock_movement(
        db=db, product=product,
        quantity=qty,
        movement_type="manufacturing_production",
        reference_type="manufacturing_order",
        reference_id=mo.id,
        reference_number=mo.mo_number,
        notes=f"Production completion for MO {mo.mo_number}",
        user_id=current_user.id,
    )

    mo.produced_qty = qty
    mo.status = "completed"
    mo.actual_end = datetime.utcnow()
    for wo in mo.work_orders:
        wo.status = "completed"
        wo.completed_at = datetime.utcnow()

    db.commit()
    return {"message": "Manufacturing order completed", "produced_qty": qty}


@router.get("/work-orders", response_model=dict)
def list_work_orders(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    mo_id: Optional[int] = None, status: Optional[str] = None,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    q = db.query(WorkOrder)
    if mo_id:
        q = q.filter(WorkOrder.manufacturing_order_id == mo_id)
    if status:
        q = q.filter(WorkOrder.status == status)
    result = paginate(q.order_by(WorkOrder.created_at.desc()), page, page_size)
    result["items"] = [WorkOrderOut.model_validate(wo) for wo in result["items"]]
    return result
