from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional, List
import os, shutil, uuid
from ..database import get_db
from ..models.product import Product, Category
from ..models.user import User
from ..schemas.product import ProductCreate, ProductUpdate, ProductOut, CategoryCreate, CategoryOut, StockAdjustment
from ..utils.helpers import paginate, get_next_sequence
from ..middleware.auth_middleware import get_current_user, require_permission
from ..services.inventory_service import record_stock_movement
from ..config import settings

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/", response_model=dict)
def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    low_stock: Optional[bool] = None,
    is_active: Optional[bool] = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Product)
    if is_active is not None:
        query = query.filter(Product.is_active == is_active)
    if search:
        query = query.filter(
            Product.product_name.ilike(f"%{search}%") | Product.product_code.ilike(f"%{search}%")
        )
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if low_stock:
        query = query.filter(Product.on_hand_qty <= Product.reorder_point)
    result = paginate(query.order_by(Product.product_code), page, page_size)
    result["items"] = [ProductOut.model_validate(p) for p in result["items"]]
    return result


@router.post("/", response_model=ProductOut, status_code=201)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("products", "create")),
):
    if db.query(Product).filter(Product.product_code == data.product_code).first():
        raise HTTPException(status_code=400, detail="Product code already exists")
    product = Product(**data.model_dump(), created_by=current_user.id)
    db.add(product)
    db.commit()
    db.refresh(product)
    return ProductOut.model_validate(product)


@router.get("/categories", response_model=List[CategoryOut])
def list_categories(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Category).all()


@router.post("/categories", response_model=CategoryOut, status_code=201)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("products", "create")),
):
    cat = Category(**data.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.get("/low-stock", response_model=List[ProductOut])
def get_low_stock(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    products = db.query(Product).filter(
        Product.on_hand_qty <= Product.reorder_point,
        Product.is_active == True
    ).all()
    return [ProductOut.model_validate(p) for p in products]


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductOut.model_validate(product)


@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("products", "update")),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return ProductOut.model_validate(product)


@router.delete("/{product_id}", status_code=204)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("products", "delete")),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.is_active = False
    db.commit()


@router.post("/{product_id}/adjust-stock")
def adjust_stock(
    product_id: int,
    data: StockAdjustment,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("inventory", "adjust")),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    record_stock_movement(
        db=db,
        product=product,
        quantity=float(data.quantity),
        movement_type="manual_adjustment",
        reference_type="manual",
        reference_id=product_id,
        reference_number=f"ADJ-{product_id}",
        notes=data.notes,
        user_id=current_user.id,
    )
    db.commit()
    return {"message": "Stock adjusted successfully", "new_quantity": float(product.on_hand_qty)}


@router.post("/{product_id}/upload-image")
async def upload_image(
    product_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("products", "update")),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    ext = os.path.splitext(file.filename)[1]
    if ext.lower() not in [".jpg", ".jpeg", ".png", ".webp"]:
        raise HTTPException(status_code=400, detail="Only image files allowed")
    upload_dir = os.path.join(settings.UPLOAD_DIR, "products")
    os.makedirs(upload_dir, exist_ok=True)
    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(upload_dir, filename)
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)
    product.image_path = f"/uploads/products/{filename}"
    db.commit()
    return {"image_path": product.image_path}
