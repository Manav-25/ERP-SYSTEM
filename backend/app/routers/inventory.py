from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..models.inventory import StockLedger
from ..models.product import Product
from ..models.user import User
from ..utils.helpers import paginate
from ..middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get("/ledger", response_model=dict)
def get_stock_ledger(
    page: int = Query(1, ge=1),
    page_size: int = Query(30, ge=1, le=200),
    product_id: Optional[int] = None,
    movement_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(StockLedger)
    if product_id:
        q = q.filter(StockLedger.product_id == product_id)
    if movement_type:
        q = q.filter(StockLedger.movement_type == movement_type)
    result = paginate(q.order_by(StockLedger.movement_date.desc()), page, page_size)
    items = []
    for entry in result["items"]:
        items.append({
            "id": entry.id,
            "product_id": entry.product_id,
            "product_name": entry.product.product_name if entry.product else None,
            "product_code": entry.product.product_code if entry.product else None,
            "movement_date": entry.movement_date.isoformat() if entry.movement_date else None,
            "movement_type": entry.movement_type,
            "quantity": float(entry.quantity),
            "balance_qty": float(entry.balance_qty),
            "unit_cost": float(entry.unit_cost or 0),
            "reference_number": entry.reference_number,
            "notes": entry.notes,
        })
    result["items"] = items
    return result


@router.get("/stock-summary", response_model=list)
def get_stock_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    products = db.query(Product).filter(Product.is_active == True).all()
    summary = []
    for p in products:
        summary.append({
            "id": p.id,
            "product_code": p.product_code,
            "product_name": p.product_name,
            "on_hand_qty": float(p.on_hand_qty or 0),
            "reserved_qty": float(p.reserved_qty or 0),
            "free_qty": p.free_qty,
            "reorder_point": float(p.reorder_point or 0),
            "is_low_stock": p.is_low_stock,
            "inventory_value": float(p.on_hand_qty or 0) * float(p.cost_price or 0),
            "unit_of_measure": p.unit_of_measure,
        })
    return summary


@router.get("/valuation")
def get_inventory_valuation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    products = db.query(Product).filter(Product.is_active == True).all()
    total_value = sum(float(p.on_hand_qty or 0) * float(p.cost_price or 0) for p in products)
    low_stock_count = sum(1 for p in products if p.is_low_stock)
    return {
        "total_inventory_value": round(total_value, 2),
        "total_products": len(products),
        "low_stock_count": low_stock_count,
        "currency": "INR",
    }
