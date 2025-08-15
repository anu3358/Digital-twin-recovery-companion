from database import engine, Base, SessionLocal
from models import User, PatientProfile
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def upsert_user(db, email, password, role, full_name):
    u = db.query(User).filter(User.email==email).first()
    if u:
        return u
    u = User(email=email, hashed_password=pwd_context.hash(password), role=role, full_name=full_name)
    db.add(u); db.commit(); db.refresh(u)
    if role == 'patient':
        p = PatientProfile(user_id=u.id, demographics={"age": 45, "sex":"M"}, medical_history="Post-orthopedic surgery")
        db.add(p); db.commit()
    return u

def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    upsert_user(db, "admin@dtc.local", "changeme", "admin", "Administrator")
    upsert_user(db, "clinician@example.com", "changeme", "clinician", "Dr. Cohen")
    upsert_user(db, "patient@example.com", "changeme", "patient", "Anita Sharma")
    db.close()
    print("Seed complete. Users ready.")

if __name__ == "__main__":
    main()
