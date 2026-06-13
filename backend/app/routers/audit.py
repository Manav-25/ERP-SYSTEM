from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..models.audit import AuditLog
from ..models.user import User
from ..utils.helpers import paginate
from ..middleware.auth_middleware import require_roles

router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get("/logs", response_model=dict)
def get_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(30, ge=1, le=200),
    module: Optional[str] = None,
    action: Optional[str] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    q = db.query(AuditLog)
    if module:
        q = q.filter(AuditLog.module == module)
    if action:
        q = q.filter(AuditLog.action == action)
    if user_id:
        q = q.filter(AuditLog.user_id == user_id)
    result = paginate(q.order_by(AuditLog.created_at.desc()), page, page_size)
    result["items"] = [
        {
            "id": log.id,
            "username": log.username,
            "action": log.action,
            "module": log.module,
            "record_type": log.record_type,
            "record_id": log.record_id,
            "ip_address": log.ip_address,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }
        for log in result["items"]
    ]
    return result
