from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User, UserRole, Role, RolePermission, Permission
from ..utils.security import decode_token

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    user = db.query(User).filter(User.id == int(user_id), User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
    return user


def get_user_permissions(user: User, db: Session) -> list[str]:
    role_ids = [ur.role_id for ur in user.roles]
    permissions = (
        db.query(Permission)
        .join(RolePermission, Permission.id == RolePermission.permission_id)
        .filter(RolePermission.role_id.in_(role_ids))
        .all()
    )
    return [f"{p.module}:{p.action}" for p in permissions]


def get_user_roles(user: User) -> list[str]:
    return [ur.role.name for ur in user.roles]


def require_permission(module: str, action: str):
    def checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        # Admin bypasses all permission checks
        user_roles = get_user_roles(current_user)
        if "admin" in user_roles:
            return current_user
        permissions = get_user_permissions(current_user, db)
        if f"{module}:{action}" not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {module}:{action}",
            )
        return current_user
    return checker


def require_roles(*role_names: str):
    def checker(current_user: User = Depends(get_current_user)):
        user_roles = get_user_roles(current_user)
        if not any(r in user_roles for r in role_names):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role",
            )
        return current_user
    return checker
