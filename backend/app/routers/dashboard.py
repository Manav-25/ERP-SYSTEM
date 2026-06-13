from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta
from ..database import get_db
from ..models.product import Product
from ..models.sales import SalesOrder, SalesOrderItem
from ..models.purchase import PurchaseOrder
from ..models.manufacturing import ManufacturingOrder
from ..models.inventory import StockLedger
from ..models.audit import Notification
from ..models.user import User
from ..middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = date.today()
    thirty_days_ago = today - timedelta(days=30)

    total_products = db.query(Product).filter(Product.is_active == True).count()
    low_stock_products = db.query(Product).filter(
        Product.on_hand_qty <= Product.reorder_point,
        Product.is_active == True
    ).count()

    total_so = db.query(SalesOrder).count()
    pending_so = db.query(SalesOrder).filter(SalesOrder.status.in_(["draft", "confirmed", "partially_delivered"])).count()
    so_this_month = db.query(SalesOrder).filter(SalesOrder.order_date >= thirty_days_ago).count()

    total_po = db.query(PurchaseOrder).count()
    pending_po = db.query(PurchaseOrder).filter(PurchaseOrder.status.in_(["draft", "confirmed", "partially_received"])).count()

    total_mo = db.query(ManufacturingOrder).count()
    active_mo = db.query(ManufacturingOrder).filter(
        ManufacturingOrder.status.in_(["confirmed", "in_progress"])
    ).count()

    delayed_orders = db.query(SalesOrder).filter(
        SalesOrder.expected_delivery_date < today,
        SalesOrder.status.in_(["confirmed", "partially_delivered"])
    ).count()

    inventory_value = db.query(
        func.sum(Product.on_hand_qty * Product.cost_price)
    ).filter(Product.is_active == True).scalar() or 0

    so_value_month = db.query(
        func.sum(SalesOrder.total_amount)
    ).filter(SalesOrder.order_date >= thirty_days_ago).scalar() or 0

    po_value_month = db.query(
        func.sum(PurchaseOrder.total_amount)
    ).filter(PurchaseOrder.order_date >= thirty_days_ago).scalar() or 0

    return {
        "products": {
            "total": total_products,
            "low_stock": low_stock_products,
        },
        "sales": {
            "total": total_so,
            "pending": pending_so,
            "this_month": so_this_month,
            "value_this_month": round(float(so_value_month), 2),
        },
        "purchase": {
            "total": total_po,
            "pending": pending_po,
            "value_this_month": round(float(po_value_month), 2),
        },
        "manufacturing": {
            "total": total_mo,
            "active": active_mo,
        },
        "delayed_orders": delayed_orders,
        "inventory_value": round(float(inventory_value), 2),
    }


@router.get("/sales-chart")
def get_sales_chart(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from_date = date.today() - timedelta(days=days)
    rows = (
        db.query(
            SalesOrder.order_date,
            func.count(SalesOrder.id).label("count"),
            func.sum(SalesOrder.total_amount).label("amount"),
        )
        .filter(SalesOrder.order_date >= from_date)
        .group_by(SalesOrder.order_date)
        .order_by(SalesOrder.order_date)
        .all()
    )
    return [
        {"date": str(r.order_date), "count": r.count, "amount": round(float(r.amount or 0), 2)}
        for r in rows
    ]


@router.get("/inventory-chart")
def get_inventory_chart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from ..models.product import Category
    rows = (
        db.query(
            Category.name.label("category"),
            func.count(Product.id).label("count"),
            func.sum(Product.on_hand_qty * Product.cost_price).label("value"),
        )
        .join(Product, Product.category_id == Category.id)
        .filter(Product.is_active == True)
        .group_by(Category.name)
        .all()
    )
    return [
        {"category": r.category, "count": r.count, "value": round(float(r.value or 0), 2)}
        for r in rows
    ]


@router.get("/recent-activity")
def get_recent_activity(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    recent_so = db.query(SalesOrder).order_by(SalesOrder.created_at.desc()).limit(5).all()
    recent_po = db.query(PurchaseOrder).order_by(PurchaseOrder.created_at.desc()).limit(5).all()
    activities = []
    for so in recent_so:
        activities.append({
            "type": "sales_order",
            "number": so.order_number,
            "status": so.status,
            "amount": float(so.total_amount or 0),
            "date": so.created_at.isoformat() if so.created_at else None,
        })
    for po in recent_po:
        activities.append({
            "type": "purchase_order",
            "number": po.order_number,
            "status": po.status,
            "amount": float(po.total_amount or 0),
            "date": po.created_at.isoformat() if po.created_at else None,
        })
    activities.sort(key=lambda x: x["date"] or "", reverse=True)
    return activities[:limit]


@router.get("/notifications")
def get_notifications(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notifs = (
        db.query(Notification)
        .filter((Notification.user_id == current_user.id) | (Notification.user_id == None))
        .order_by(Notification.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "type": n.type,
            "category": n.category,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat() if n.created_at else None,
        }
        for n in notifs
    ]


@router.post("/notifications/{notif_id}/read")
def mark_notification_read(
    notif_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notif = db.query(Notification).filter(Notification.id == notif_id).first()
    if notif:
        notif.is_read = True
        db.commit()
    return {"message": "Marked as read"}
