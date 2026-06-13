from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models.user import User, UserRole, Role
from ..schemas.user import UserCreate, UserUpdate, UserOut, RoleOut
from ..utils.security import get_password_hash
from ..utils.helpers import paginate
from ..middleware.auth_middleware import get_current_user, require_roles

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=dict)
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    query = db.query(User)
    if search:
        query = query.filter(
            User.username.ilike(f"%{search}%") | User.email.ilike(f"%{search}%") | User.full_name.ilike(f"%{search}%")
        )
    result = paginate(query.order_by(User.created_at.desc()), page, page_size)
    result["items"] = [UserOut.model_validate(u) for u in result["items"]]
    return result


@router.post("/", response_model=UserOut, status_code=201)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    user = User(
        username=data.username,
        email=data.email,
        password_hash=get_password_hash(data.password),
        full_name=data.full_name,
        phone=data.phone,
    )
    db.add(user)
    db.flush()
    for role_id in data.role_ids:
        role = db.query(Role).filter(Role.id == role_id).first()
        if role:
            db.add(UserRole(user_id=user.id, role_id=role_id))
    db.commit()
    db.refresh(user)
    return UserOut.model_validate(user)


@router.get("/roles", response_model=List[RoleOut])
def list_roles(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Role).all()


@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserOut.model_validate(user)


@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if data.full_name is not None:
        user.full_name = data.full_name
    if data.phone is not None:
        user.phone = data.phone
    if data.is_active is not None:
        user.is_active = data.is_active
    if data.role_ids is not None:
        db.query(UserRole).filter(UserRole.user_id == user_id).delete()
        for role_id in data.role_ids:
            db.add(UserRole(user_id=user_id, role_id=role_id))
    db.commit()
    db.refresh(user)
    return UserOut.model_validate(user)


@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    db.delete(user)
    db.commit()
