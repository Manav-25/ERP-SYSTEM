from sqlalchemy.orm import Session
from ..models.product import Product
from ..models.inventory import StockLedger, StockReservation


def record_stock_movement(
    db: Session,
    product: Product,
    quantity: float,
    movement_type: str,
    reference_type: str,
    reference_id: int,
    reference_number: str,
    notes: str = None,
    user_id: int = None,
):
    product.on_hand_qty = float(product.on_hand_qty or 0) + quantity
    new_balance = float(product.on_hand_qty)

    ledger = StockLedger(
        product_id=product.id,
        movement_type=movement_type,
        quantity=quantity,
        balance_qty=new_balance,
        unit_cost=float(product.cost_price or 0),
        reference_type=reference_type,
        reference_id=reference_id,
        reference_number=reference_number,
        notes=notes,
        created_by=user_id,
    )
    db.add(ledger)
    return ledger


def reserve_stock(
    db: Session,
    product: Product,
    quantity: float,
    reservation_type: str,
    reference_id: int,
    reference_number: str,
):
    reservation = StockReservation(
        product_id=product.id,
        reserved_qty=quantity,
        reservation_type=reservation_type,
        reference_id=reference_id,
        reference_number=reference_number,
    )
    product.reserved_qty = float(product.reserved_qty or 0) + quantity
    db.add(reservation)
    return reservation


def release_reservation(
    db: Session,
    product: Product,
    reservation_type: str,
    reference_id: int,
):
    from datetime import datetime
    reservations = db.query(StockReservation).filter(
        StockReservation.product_id == product.id,
        StockReservation.reservation_type == reservation_type,
        StockReservation.reference_id == reference_id,
        StockReservation.is_released == False,
    ).all()
    for r in reservations:
        r.is_released = True
        r.released_at = datetime.utcnow()
        product.reserved_qty = max(0, float(product.reserved_qty or 0) - float(r.reserved_qty))
