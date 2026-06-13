from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from ..database import get_db
from ..models.sales import SalesOrder, SalesOrderItem, Delivery, DeliveryItem
from ..models.customer import Customer
from ..models.product import Product
from ..models.user import User
from ..schemas.sales import (
    CustomerCreate, CustomerUpdate, CustomerOut,
    SalesOrderCreate, SalesOrderUpdate, SalesOrderOut,
    DeliveryCreate, DeliveryOut
)
from ..utils.helpers import paginate, get_next_sequence
from ..middleware.auth_middleware import get_current_user, require_permission
from ..services.inventory_service import record_stock_movement, reserve_stock
from ..services.procurement_service import trigger_procurement

router = APIRouter(prefix="/sales", tags=["Sales"])


# ── Customers ──────────────────────────────────────────────────────────────────

@router.get("/customers", response_model=dict)
def list_customers(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    q = db.query(Customer).filter(Customer.is_active == True)
    if search:
        q = q.filter(Customer.company_name.ilike(f"%{search}%"))
    result = paginate(q.order_by(Customer.company_name), page, page_size)
    result["items"] = [CustomerOut.model_validate(c) for c in result["items"]]
    return result


@router.post("/customers", response_model=CustomerOut, status_code=201)
def create_customer(
    data: CustomerCreate, db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("sales", "create")),
):
    code = get_next_sequence(db, "CUST")
    customer = Customer(**data.model_dump(), customer_code=code)
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return CustomerOut.model_validate(customer)


@router.get("/customers/{customer_id}", response_model=CustomerOut)
def get_customer(customer_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    c = db.query(Customer).filter(Customer.id == customer_id).first()
    if not c:
        raise HTTPException(404, "Customer not found")
    return CustomerOut.model_validate(c)


@router.put("/customers/{customer_id}", response_model=CustomerOut)
def update_customer(
    customer_id: int, data: CustomerUpdate,
    db: Session = Depends(get_db), current_user: User = Depends(require_permission("sales", "update")),
):
    c = db.query(Customer).filter(Customer.id == customer_id).first()
    if not c:
        raise HTTPException(404, "Customer not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(c, k, v)
    db.commit()
    db.refresh(c)
    return CustomerOut.model_validate(c)


# ── Sales Orders ───────────────────────────────────────────────────────────────

@router.get("/orders", response_model=dict)
def list_orders(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None, customer_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    q = db.query(SalesOrder)
    if status:
        q = q.filter(SalesOrder.status == status)
    if customer_id:
        q = q.filter(SalesOrder.customer_id == customer_id)
    if search:
        q = q.filter(SalesOrder.order_number.ilike(f"%{search}%"))
    result = paginate(q.order_by(SalesOrder.created_at.desc()), page, page_size)
    result["items"] = [SalesOrderOut.model_validate(o) for o in result["items"]]
    return result


@router.post("/orders", response_model=SalesOrderOut, status_code=201)
def create_order(
    data: SalesOrderCreate, db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("sales", "create")),
):
    customer = db.query(Customer).filter(Customer.id == data.customer_id).first()
    if not customer:
        raise HTTPException(404, "Customer not found")

    order_number = get_next_sequence(db, "SO")
    so = SalesOrder(
        order_number=order_number,
        customer_id=data.customer_id,
        order_date=data.order_date,
        expected_delivery_date=data.expected_delivery_date,
        notes=data.notes,
        created_by=current_user.id,
    )
    db.add(so)
    db.flush()

    subtotal = Decimal("0.00")
    for item_data in data.items:
        product = db.query(Product).filter(Product.id == item_data.product_id).first()
        if not product:
            raise HTTPException(404, f"Product {item_data.product_id} not found")
        discount = item_data.ordered_qty * item_data.unit_price * item_data.discount_pct / 100
        tax = (item_data.ordered_qty * item_data.unit_price - discount) * item_data.tax_pct / 100
        line_total = item_data.ordered_qty * item_data.unit_price - discount + tax
        item = SalesOrderItem(
            sales_order_id=so.id,
            product_id=item_data.product_id,
            ordered_qty=item_data.ordered_qty,
            unit_price=item_data.unit_price,
            discount_pct=item_data.discount_pct,
            tax_pct=item_data.tax_pct,
            line_total=line_total,
        )
        db.add(item)
        subtotal += line_total

    so.subtotal = subtotal
    so.total_amount = subtotal
    db.commit()
    db.refresh(so)
    return SalesOrderOut.model_validate(so)


@router.get("/orders/{order_id}", response_model=SalesOrderOut)
def get_order(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    so = db.query(SalesOrder).filter(SalesOrder.id == order_id).first()
    if not so:
        raise HTTPException(404, "Sales order not found")
    return SalesOrderOut.model_validate(so)


@router.post("/orders/{order_id}/confirm")
def confirm_order(
    order_id: int, db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("sales", "update")),
):
    so = db.query(SalesOrder).filter(SalesOrder.id == order_id).first()
    if not so:
        raise HTTPException(404, "Sales order not found")
    if so.status != "draft":
        raise HTTPException(400, f"Cannot confirm order in status: {so.status}")

    procurement_results = []
    for item in so.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        free_qty = float(product.on_hand_qty or 0) - float(product.reserved_qty or 0)
        reserve_qty = min(float(item.ordered_qty), free_qty)

        if reserve_qty > 0:
            reserve_stock(db, product, reserve_qty, "sales_order", so.id, so.order_number)

        if float(item.ordered_qty) > free_qty:
            result = trigger_procurement(
                db=db, product=product,
                required_qty=float(item.ordered_qty),
                reference_so_id=so.id, so_number=so.order_number,
                user_id=current_user.id,
            )
            if result.get("triggered"):
                procurement_results.append(result)

    so.status = "confirmed"
    so.confirmed_by = current_user.id
    so.confirmed_at = datetime.utcnow()
    db.commit()
    return {"message": "Order confirmed", "order_number": so.order_number, "procurement": procurement_results}


@router.post("/orders/{order_id}/cancel")
def cancel_order(
    order_id: int, db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("sales", "update")),
):
    so = db.query(SalesOrder).filter(SalesOrder.id == order_id).first()
    if not so:
        raise HTTPException(404, "Sales order not found")
    if so.status in ("fully_delivered", "cancelled"):
        raise HTTPException(400, f"Cannot cancel order in status: {so.status}")

    from ..services.inventory_service import release_reservation
    for item in so.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        release_reservation(db, product, "sales_order", so.id)

    so.status = "cancelled"
    db.commit()
    return {"message": "Order cancelled"}


# ── Deliveries ─────────────────────────────────────────────────────────────────

@router.post("/deliveries", response_model=DeliveryOut, status_code=201)
def create_delivery(
    data: DeliveryCreate, db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("sales", "update")),
):
    so = db.query(SalesOrder).filter(SalesOrder.id == data.sales_order_id).first()
    if not so:
        raise HTTPException(404, "Sales order not found")
    if so.status not in ("confirmed", "partially_delivered"):
        raise HTTPException(400, "Sales order must be confirmed to deliver")

    delivery_number = get_next_sequence(db, "DEL")
    delivery = Delivery(
        delivery_number=delivery_number,
        sales_order_id=so.id,
        delivery_date=data.delivery_date,
        notes=data.notes,
        status="delivered",
        created_by=current_user.id,
    )
    db.add(delivery)
    db.flush()

    for item_data in data.items:
        product = db.query(Product).filter(Product.id == item_data.product_id).first()
        so_item = db.query(SalesOrderItem).filter(SalesOrderItem.id == item_data.sales_order_item_id).first()

        if not product or not so_item:
            raise HTTPException(404, "Product or SO item not found")

        remaining = float(so_item.ordered_qty) - float(so_item.delivered_qty)
        if float(item_data.delivered_qty) > remaining:
            raise HTTPException(400, f"Deliver qty exceeds remaining for product {product.product_name}")

        db.add(DeliveryItem(
            delivery_id=delivery.id,
            sales_order_item_id=so_item.id,
            product_id=product.id,
            delivered_qty=item_data.delivered_qty,
        ))
        so_item.delivered_qty = float(so_item.delivered_qty) + float(item_data.delivered_qty)

        record_stock_movement(
            db=db, product=product,
            quantity=-float(item_data.delivered_qty),
            movement_type="sales_delivery",
            reference_type="delivery",
            reference_id=delivery.id,
            reference_number=delivery_number,
            notes=f"Delivery for SO {so.order_number}",
            user_id=current_user.id,
        )
        from ..services.inventory_service import release_reservation
        release_reservation(db, product, "sales_order", so.id)

    total_ordered = sum(float(i.ordered_qty) for i in so.items)
    total_delivered = sum(float(i.delivered_qty) for i in so.items)
    if total_delivered >= total_ordered:
        so.status = "fully_delivered"
    else:
        so.status = "partially_delivered"

    db.commit()
    db.refresh(delivery)
    return DeliveryOut.model_validate(delivery)


@router.get("/deliveries", response_model=dict)
def list_deliveries(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    sales_order_id: Optional[int] = None,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    q = db.query(Delivery)
    if sales_order_id:
        q = q.filter(Delivery.sales_order_id == sales_order_id)
    result = paginate(q.order_by(Delivery.created_at.desc()), page, page_size)
    result["items"] = [DeliveryOut.model_validate(d) for d in result["items"]]
    return result
