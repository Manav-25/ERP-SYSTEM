from sqlalchemy.orm import Session
from ..models.audit import SequenceCounter
import secrets
import string


def get_next_sequence(db: Session, prefix: str) -> str:
    counter = db.query(SequenceCounter).filter(SequenceCounter.prefix == prefix).with_for_update().first()
    if not counter:
        counter = SequenceCounter(prefix=prefix, last_number=0)
        db.add(counter)
    counter.last_number += 1
    db.flush()
    return f"{prefix}-{counter.last_number:05d}"


def generate_reset_token(length: int = 32) -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def paginate(query, page: int = 1, page_size: int = 20):
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size,
    }
