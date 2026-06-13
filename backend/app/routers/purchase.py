from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from ..database import get_db
from ..models.purchase import PurchaseOrder, PurchaseOrderItem, GoodsReceipt, GoodsReceiptItem
from ..models.vendor import Vendor
from ..models.product import Product
from ..models.user import User
from ..schemas.purchase import (
    VendorCreate, VendorOut,
    PurchaseOrderCreate, PurchaseOrderOut,
    GoodsReceiptCreate, GoodsReceiptOut,
)
from ..utils.helpers import paginate, get_next_sequence
from ..middleware.auth_middleware import get_current_user, require_permission
from ..services.inventory_service import record_stock_movement

router = APIRouter(prefix="/purchase", tags=["Purchase"])


# ── Vendors ────────────────────────────────────────────────────────────────────

@router.get("/vendors", response_model=dict)
def list_vendors(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    q = db.query(Vendor).filter(Vendor.is_active == True)
    if search:
        q = q.filter(Vendor.company_name.ilike(f"%{search}%"))
    result = paginate(q.order_by(Vendor.company_name), page, page_size)
    result["items"] = [VendorOut.model_validate(v) for v in result["items"]]
    return result


@router.post("/vendors", response_model=VendorOut, status_code=201)
def create_vendor(
    data: VendorCreate, db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("purchase", "create")),
):
    code = get_next_sequence(db, "VEND")
    vendor = Vendor(**data.model_dump(), vendor_code=code)
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return VendorOut.model_validate(vendor)


@router.get("/vendors/{vendor_id}", response_model=VendorOut)
def get_vendor(vendor_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    v = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not v:
        raise HTTPException(404, "Vendor not found")
    return VendorOut.model_validate(v)


# ── Purchase Orders ────────────────────────────────────────────────────────────

@router.get("/orders", response_model=dict)
def list_orders(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None, vendor_id: Optional[int] = None,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    q = db.query(PurchaseOrder)
    if status:
        q = q.filter(PurchaseOrder.status == status)
    if vendor_id:
        q = q.filter(PurchaseOrder.vendor_id == vendor_id)
    result = paginate(q.order_by(PurchaseOrder.created_at.desc()), page, page_size)
    result["items"] = [PurchaseOrderOut.model_validate(o) for o in result["items"]]
    return result


@router.post("/orders", response_model=PurchaseOrderOut, status_code=201)
def create_order(
    data: PurchaseOrderCreate, db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("purchase", "create")),
):
    vendor = db.query(Vendor).filter(Vendor.id == data.vendor_id).first()
    if not vendor:
        raise HTTPException(404, "Vendor not found")

    order_number = get_next_sequence(db, "PO")
    po = PurchaseOrder(
        order_number=order_number,
        vendor_id=data.vendor_id,
        order_date=data.order_date,
        expected_receipt_date=data.expected_receipt_date,
        notes=data.notes,
        created_by=current_user.id,
    )
    db.add(po)
    db.flush()

    subtotal = Decimal("0.00")
    tax_total = Decimal("0.00")
    for item_data in data.items:
        product = db.query(Product).filter(Product.id == item_data.product_id).first()
        if not product:
            raise HTTPException(404, f"Product {item_data.product_id} not found")
        line_total = item_data.ordered_qty * item_data.unit_price
        tax = line_total * item_data.tax_pct / 100
        db.add(PurchaseOrderItem(
            purchase_order_id=po.id,
            product_id=item_data.product_id,
            ordered_qty=item_data.ordered_qty,
            unit_price=item_data.unit_price,
            tax_pct=item_data.tax_pct,
            line_total=line_total + tax,
        ))
        subtotal += line_total
        tax_total += tax

    po.subtotal = subtotal
    po.tax_amount = tax_total
    po.total_amount = subtotal + tax_total
    db.commit()
    db.refresh(po)
    return PurchaseOrderOut.model_validate(po)


@router.get("/orders/{order_id}", response_model=PurchaseOrderOut)
def get_order(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).first()
    if not po:
        raise HTTPException(404, "Purchase order not found")
    return PurchaseOrderOut.model_validate(po)


@router.post("/orders/{order_id}/confirm")
def confirm_order(
    order_id: int, db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("purchase", "update")),
):
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).first()
    if not po:
        raise HTTPException(404, "Purchase order not found")
    if po.status != "draft":
        raise HTTPException(400, f"Cannot confirm PO in status: {po.status}")
    po.status = "confirmed"
    po.confirmed_at = datetime.utcnow()
    db.commit()
    return {"message": "Purchase order confirmed", "order_number": po.order_number}


@router.post("/orders/{order_id}/cancel")
def cancel_order(
    order_id: int, db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("purchase", "update")),
):
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).first()
    if not po:
        raise HTTPException(404, "Purchase order not found")
    if po.status in ("fully_received", "cancelled"):
        raise HTTPException(400, f"Cannot cancel PO in status: {po.status}")
    po.status = "cancelled"
    db.commit()
    return {"message": "Purchase order cancelled"}


# ── Goods Receipts ─────────────────────────────────────────────────────────────

@router.post("/receipts", response_model=GoodsReceiptOut, status_code=201)
def create_receipt(
    data: GoodsReceiptCreate, db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("purchase", "update")),
):
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == data.purchase_order_id).first()
    if not po:
        raise HTTPException(404, "Purchase order not found")
    if po.status not in ("confirmed", "partially_received"):
        raise HTTPException(400, "PO must be confirmed to receive")

    receipt_number = get_next_sequence(db, "GR")
    receipt = GoodsReceipt(
        receipt_number=receipt_number,
        purchase_order_id=po.id,
        receipt_date=data.receipt_date,
        notes=data.notes,
        created_by=current_user.id,
    )
    db.add(receipt)
    db.flush()

    for item_data in data.items:
        product = db.query(Product).filter(Product.id == item_data.product_id).first()
        po_item = db.query(PurchaseOrderItem).filter(PurchaseOrderItem.id == item_data.purchase_order_item_id).first()

        if not product or not po_item:
            raise HTTPException(404, "Product or PO item not found")

        db.add(GoodsReceiptItem(
            receipt_id=receipt.id,
            purchase_order_item_id=po_item.id,
            product_id=product.id,
            received_qty=item_data.received_qty,
        ))
        po_item.received_qty = float(po_item.received_qty) + float(item_data.received_qty)

        record_stock_movement(
            db=db, product=product,
            quantity=float(item_data.received_qty),
            movement_type="purchase_receipt",
            reference_type="goods_receipt",
            reference_id=receipt.id,
            reference_number=receipt_number,
            notes=f"Goods receipt for PO {po.order_number}",
            user_id=current_user.id,
        )

    total_ordered = sum(float(i.ordered_qty) for i in po.items)
    total_received = sum(float(i.received_qty) for i in po.items)
    if total_received >= total_ordered:
        po.status = "fully_received"
    else:
        po.status = "partially_received"

    db.commit()
    db.refresh(receipt)
    return GoodsReceiptOut.model_validate(receipt)


@router.get("/receipts", response_model=dict)
def list_receipts(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    purchase_order_id: Optional[int] = None,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    q = db.query(GoodsReceipt)
    if purchase_order_id:
        q = q.filter(GoodsReceipt.purchase_order_id == purchase_order_id)
    result = paginate(q.order_by(GoodsReceipt.created_at.desc()), page, page_size)
    result["items"] = [GoodsReceiptOut.model_validate(r) for r in result["items"]]
    return result
