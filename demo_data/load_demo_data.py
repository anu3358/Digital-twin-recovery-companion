import json, os, datetime
from database import engine, SessionLocal, Base
from models import User, PatientProfile, SensorStream, Prediction, AuditLog
from passlib.context import CryptContext

pwd = CryptContext(schemes=['bcrypt'], deprecated='auto')

BASE = os.path.join(os.path.dirname(__file__), 'demo_data')
def load_users():
    db = SessionLocal()
    with open(os.path.join(BASE,'users.json')) as f:
        data = json.load(f)
    # admin
    admin = data['admin']
    if not db.query(User).filter(User.email==admin['email']).first():
        u = User(email=admin['email'], hashed_password=pwd.hash(admin['password']), full_name=admin['full_name'], role='admin')
        db.add(u); db.commit(); db.refresh(u)
    # clinician
    cl = data['clinician']
    if not db.query(User).filter(User.email==cl['email']).first():
        u = User(email=cl['email'], hashed_password=pwd.hash(cl['password']), full_name=cl['full_name'], role='clinician')
        db.add(u); db.commit(); db.refresh(u)
    # patients
    for p in data['patients']:
        if not db.query(User).filter(User.email==p['email']).first():
            u = User(email=p['email'], hashed_password=pwd.hash(p['password']), full_name=p['full_name'], role='patient')
            db.add(u); db.commit(); db.refresh(u)
            # create profile
            prof = PatientProfile(user_id=u.id, demographics={'age': p['age'], 'sex': p['sex']}, medical_history=p['history'])
            db.add(prof); db.commit()
    db.close()

def load_streams():
    db = SessionLocal()
    with open(os.path.join(BASE,'sensor_streams.json')) as f:
        streams = json.load(f)
    # map patient_ref (1..n) to actual patient_profile ids by order of creation
    patients = db.query(PatientProfile).all()
    mapping = {i+1: patients[i].id for i in range(len(patients))}
    for s in streams:
        pid = mapping.get(s['patient_ref'])
        if not pid: continue
        p = SensorStream(patient_id=pid, timestamp=datetime.datetime.fromisoformat(s['timestamp']), sensor_type=s['sensor_type'], payload=s['payload'])
        db.add(p)
    db.commit(); db.close()

def load_predictions():
    db = SessionLocal()
    with open(os.path.join(BASE,'predictions.json')) as f:
        preds = json.load(f)
    patients = db.query(PatientProfile).all()
    mapping = {i+1: patients[i].id for i in range(len(patients))}
    for p in preds:
        pid = mapping.get(p['patient_ref'])
        if not pid: continue
        pr = Prediction(patient_id=pid, created_at=datetime.datetime.fromisoformat(p['created_at']), model_version=p['model_version'], result=p['result'])
        db.add(pr)
    db.commit(); db.close()

def load_audits():
    db = SessionLocal()
    with open(os.path.join(BASE,'audit_logs.json')) as f:
        logs = json.load(f)
    # create entries
    for l in logs:
        if isinstance(l['user_ref'], int):
            # map to user by insertion order among patients
            user = db.query(User).filter(User.role=='patient').all()[l['user_ref']-1]
            uid = user.id
        else:
            user = db.query(User).filter(User.email==l['user_ref']).first()
            uid = user.id if user else None
        entry = AuditLog(user_id=uid, action=l['action'], metadata=l['metadata'], timestamp=datetime.datetime.fromisoformat(l['timestamp']))
        db.add(entry)
    db.commit(); db.close()

if __name__ == '__main__':
    print('Loading demo users...')
    load_users()
    print('Loading sensor streams...')
    load_streams()
    print('Loading predictions...')
    load_predictions()
    print('Loading audit logs...')
    load_audits()
    print('Demo data loaded.')
