from sqlalchemy.orm import Session
from datetime import datetime

def log_action(db: Session, user_id: int, action: str, meta: dict = None):
    from models import AuditLog
    entry = AuditLog(user_id=user_id, action=action, metadata=meta or {}, timestamp=datetime.utcnow())
    db.add(entry)
    db.commit()
