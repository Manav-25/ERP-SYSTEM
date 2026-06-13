from sqlalchemy.orm import Session
from datetime import date, timedelta
from ..models.product import Product
from ..models.purchase import PurchaseOrder, PurchaseOrderItem
from ..models.manufacturing import ManufacturingOrder, MOComponent
from ..models.vendor import Vendor
from ..models.audit import Notification, SequenceCounter
from ..utils.helpers import get_next_sequence


def trigger_procurement(
    db: Session,
    product: Product,
    required_qty: float,
    reference_so_id: int,
    so_number: str,
    user_id: int,
) -> dict:
    free_qty = float(product.on_hand_qty or 0) - float(product.reserved_qty or 0)
    shortage = required_qty - free_qty

    if shortage <= 0:
        return {"triggered": False, "reason": "Sufficient stock available"}

    result = {}
    if product.procurement_type == "purchase":
        result = _create_auto_po(db, product, shortage, reference_so_id, so_number, user_id)
    elif product.procurement_type == "manufacturing":
        result = _create_auto_mo(db, product, shortage, reference_so_id, so_number, user_id)

    _create_notification(
        db=db,
        title=f"Procurement Triggered: {product.product_name}",
        message=f"Auto-procurement created for {shortage:.2f} {product.unit_of_measure} of {product.product_name} due to SO {so_number}",
        category="procurement",
        reference_type=result.get("type"),
        reference_id=result.get("id"),
    )
    return result


def _create_auto_po(db, product, quantity, reference_so_id, so_number, user_id):
    vendor = db.query(Vendor).filter(Vendor.is_active == True).first()
    if not vendor:
        return {"triggered": False, "reason": "No active vendor found"}

    po_number = get_next_sequence(db, "PO")
    receipt_date = date.today() + timedelta(days=vendor.lead_time_days)

    po = PurchaseOrder(
        order_number=po_number,
        vendor_id=vendor.id,
        order_date=date.today(),
        expected_receipt_date=receipt_date,
        status="draft",
        auto_generated=True,
        reference_so_id=reference_so_id,
        created_by=user_id,
        notes=f"Auto-generated from SO {so_number}",
    )
    db.add(po)
    db.flush()

    line_total = quantity * float(product.cost_price or 0)
    item = PurchaseOrderItem(
        purchase_order_id=po.id,
        product_id=product.id,
        ordered_qty=quantity,
        unit_price=float(product.cost_price or 0),
        line_total=line_total,
    )
    db.add(item)
    po.total_amount = line_total
    po.subtotal = line_total
    return {"triggered": True, "type": "purchase_order", "id": po.id, "number": po_number}


def _create_auto_mo(db, product, quantity, reference_so_id, so_number, user_id):
    from ..models.bom import BOM
    bom = db.query(BOM).filter(BOM.product_id == product.id, BOM.is_active == True).first()

    mo_number = get_next_sequence(db, "MO")
    mo = ManufacturingOrder(
        mo_number=mo_number,
        product_id=product.id,
        bom_id=bom.id if bom else None,
        planned_qty=quantity,
        scheduled_start=date.today(),
        scheduled_end=date.today() + timedelta(days=7),
        status="draft",
        auto_generated=True,
        reference_so_id=reference_so_id,
        created_by=user_id,
        notes=f"Auto-generated from SO {so_number}",
    )
    db.add(mo)
    db.flush()

    if bom:
        for comp in bom.components:
            needed = float(comp.quantity) * quantity
            db.add(MOComponent(
                manufacturing_order_id=mo.id,
                product_id=comp.component_product_id,
                required_qty=needed,
            ))
    return {"triggered": True, "type": "manufacturing_order", "id": mo.id, "number": mo_number}


def _create_notification(db, title, message, category, reference_type=None, reference_id=None):
    notif = Notification(
        title=title,
        message=message,
        type="warning",
        category=category,
        reference_type=reference_type,
        reference_id=reference_id,
    )
    db.add(notif)
