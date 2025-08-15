from passlib.context import CryptContext
from models import User
from sqlalchemy.orm import Session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def authenticate(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email==email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
