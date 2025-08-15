import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from database import SessionLocal, engine, Base
from models import User, PatientProfile, SensorStream, Prediction
from util.auth import authenticate
from models.model import TwinModel

st.set_page_config(page_title="Digital-Twin Recovery Companion", layout="wide")

# Ensure DB tables exist
Base.metadata.create_all(bind=engine)

# Session state
if "user" not in st.session_state:
    st.session_state.user = None
if "role" not in st.session_state:
    st.session_state.role = None

# Sidebar (Login / User Info)
with st.sidebar:
    st.title("Digital-Twin")
    if st.session_state.user:
        st.success(f"Logged in as: {st.session_state.user.email} ({st.session_state.role})")
        if st.button("Logout", use_container_width=True):
            st.session_state.user = None
            st.session_state.role = None
            st.rerun()
    else:
        st.subheader("Login")
        email = st.text_input("Email", value="patient@example.com")
        password = st.text_input("Password", value="changeme", type="password")
        role = st.selectbox("Role", options=["patient", "clinician", "admin"])
        if st.button("Sign in", use_container_width=True):
            db = SessionLocal()
            user = authenticate(db, email, password)
            if user and (role == user.role or role == "admin"):
                st.session_state.user = user
        from audit import log_action; db = SessionLocal(); log_action(db, user.id, 'login', {'role': user.role}); db.close()
                st.session_state.role = user.role
                st.success("Login successful")
                st.experimental_rerun()
            else:
                st.error("Invalid credentials or role mismatch")
            db.close()

st.title("Digital-Twin Recovery Companion")

if not st.session_state.user:
    st.info("Please log in from the sidebar to continue.")
    st.stop()

# Role-based routing: show/hide tabs
role = st.session_state.user.role if hasattr(st.session_state.user, 'role') else 'patient'
tab_labels = []
if role == 'patient':
    tab_labels = ["Patient Dashboard", "Data Ingestion"]
elif role == 'clinician':
    tab_labels = ["Clinician Dashboard", "Data Ingestion"]
elif role == 'admin':
    tab_labels = ["Clinician Dashboard", "Data Ingestion", "Admin"]
else:
    tab_labels = ["Patient Dashboard"]
tabs = st.tabs(tab_labels)


# ---------------- Patient Dashboard ----------------
with tabs[0]:
    if role in ['clinician','admin']:
        st.subheader('Generate Patient Report')
        patient_name = st.text_input('Patient Name for Report')
        if st.button('Download PDF Report'):
            from report import generate_report
            metrics = {'Gait Speed Change %': 12.5, 'Adherence Score': 85, 'Next Recommended Step': 'Increase balance training'}
            pdf_bytes = generate_report(patient_name or 'Unknown', metrics)
            st.download_button('Download PDF', data=pdf_bytes, file_name='recovery_report.pdf', mime='application/pdf')
    st.subheader("My Recovery")
    col1, col2 = st.columns([2,1])
    with col1:
        # Generate a simple progress chart
        progress_data = pd.DataFrame({
            "day": list(range(0, 21)),
            "value": [0.4 + i*0.02 for i in range(0,21)]
        })
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=progress_data["day"], y=progress_data["value"], mode="lines", name="Recovery Score"))
        fig.update_layout(margin=dict(l=10,r=10,t=30,b=10), height=320)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### Digital Twin (3D)")
        # Simple 3D stick figure
        xs = [0, 0, -0.3, 0, 0.3, 0, 0, -0.2, 0, 0.2]
        ys = [1.8, 1.4, 1.1, 1.4, 1.1, 1.4, 0.8, 0.2, 0.8, 0.2]
        zs = [0]*10
        fig3d = go.Figure(data=[go.Scatter3d(x=xs, y=ys, z=zs, mode='lines')])
        fig3d.update_layout(scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False)),
                            margin=dict(l=10,r=10,t=10,b=10), height=320)
        st.plotly_chart(fig3d, use_container_width=True)

    with col2:
        st.markdown("#### What-if Simulation")
        extra = st.slider("Extra balance training (min/day)", 0, 30, 5)
        run = st.button("Run Simulation", use_container_width=True)
        if run:
            model = TwinModel()
            pred = model.predict(patient_id=1, scenario={"extra_minutes_balance": extra})
            from audit import log_action; log_action(SessionLocal(), st.session_state.user.id, 'prediction', {'extra_minutes': extra2});
            st.metric("Predicted gait speed Δ", f"{pred['gait_speed_change_pct']} %")
            st.metric("Adherence score", f"{pred['adherence_score']}")

        st.markdown("---")
        st.markdown("#### Report Pain / Mood")
        pain = st.slider("Pain", 0, 10, 2)
        mood = st.select_slider("Mood", options=["sad", "ok", "good"], value="ok")
        if st.button("Submit Report", use_container_width=True):
            db = SessionLocal()
            # Map user -> patient_profile
            patient_profile = db.query(PatientProfile).filter(PatientProfile.user_id==st.session_state.user.id).first()
            if not patient_profile:
                # fallback: create
                patient_profile = PatientProfile(user_id=st.session_state.user.id, demographics={}, medical_history="")
                db.add(patient_profile); db.commit(); db.refresh(patient_profile)
            s = SensorStream(patient_id=patient_profile.id, sensor_type="patient_report", payload={"pain": pain, "mood": mood})
            db.add(s); db.commit()
            db.close()
            st.success("Thanks! Your report was saved.")

# ---------------- Clinician Dashboard ----------------
with tabs[1]:
    st.subheader("Patient Oversight")
    db = SessionLocal()
    patients = db.query(PatientProfile).all()
    names = []
    ids = []
    for p in patients:
        user = db.query(User).filter(User.id==p.user_id).first()
        label = user.full_name or user.email
        names.append(label)
        ids.append(p.id)
    if not ids:
        st.info("No patients found yet. Use Admin tab to create or run seed.py.")
    else:
        pid = st.selectbox("Select Patient", options=ids, format_func=lambda i: names[ids.index(i)])
        # mock alerts
        st.markdown("#### Alerts")
        st.warning("Gait velocity below forecast for 2 consecutive days")
        st.warning("Missed physio session yesterday")

        st.markdown("#### Patient Progress")
        df = pd.DataFrame({
            "day": list(range(0, 21)),
            "value": [0.45 + i*0.018 for i in range(0,21)]
        })
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df["day"], y=df["value"], mode="lines", name="Recovery"))
        fig2.update_layout(margin=dict(l=10,r=10,t=30,b=10), height=320)
        st.plotly_chart(fig2, use_container_width=True)

    db.close()

# ---------------- Data Ingestion ----------------
with tabs[2]:
    st.subheader("Ingest Wearable CSV")
    st.write("Upload a CSV with columns: `timestamp, accel_x, accel_y, accel_z, emg, spo2, hr, step_count`. We'll compute features and store a sample in the DB.")
    uploaded = st.file_uploader("Choose CSV file", type=["csv"])
    feats_state_key = "latest_feats"
    if uploaded is not None:
        from data_ingestion import parse_and_store
        db = SessionLocal()
        # Map user->patient profile (create if missing)
        patient_profile = db.query(PatientProfile).filter(PatientProfile.user_id==st.session_state.user.id).first()
        if not patient_profile:
            patient_profile = PatientProfile(user_id=st.session_state.user.id, demographics={}, medical_history="")
            db.add(patient_profile); db.commit(); db.refresh(patient_profile)
        try:
            head_df, feats = parse_and_store(uploaded.read(), patient_profile.id, db)
            st.session_state[feats_state_key] = feats
            st.success("Data ingested! Preview below and derived features computed.")
            from audit import log_action; log_action(db, st.session_state.user.id, 'csv_upload', {'rows': len(head_df)})
            st.dataframe(head_df)
            st.json(feats)
        except Exception as e:
            st.error(f"Failed to parse CSV: {e}")
        finally:
            db.close()

    st.markdown("#### Run Prediction with Derived Features")
    extra2 = st.slider("Extra balance training (min/day)", 0, 30, 10, key="extra2")
    if st.button("Predict from Uploaded Features", use_container_width=True):
        feats = st.session_state.get(feats_state_key)
        if not feats:
            st.warning("Please upload CSV first to compute features.")
        else:
            from models.model import TwinModel
            model = TwinModel()
            res = model.predict(patient_id=1, scenario={"extra_minutes_balance": extra2}, feats=feats)
            from audit import log_action; log_action(SessionLocal(), st.session_state.user.id, 'prediction', {'extra_minutes': extra2});
            st.metric("Predicted gait speed Δ", f"{res['gait_speed_change_pct']} %")
            st.metric("Adherence score", f"{res['adherence_score']}")

# ---------------- Admin ----------------
with tabs[2]:
    st.subheader("Admin")
    db = SessionLocal()
    st.markdown("Create Clinician/Patient Users")
    full_name = st.text_input("Full name")
    email_new = st.text_input("Email")
    pw_new = st.text_input("Password", type="password")
    role_new = st.selectbox("Role", ["patient", "clinician"])

    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    if st.button("Create User", use_container_width=True):
        if not email_new or not pw_new:
            st.error("Email and password required")
        else:
            exists = db.query(User).filter(User.email==email_new).first()
            if exists:
                st.error("Email already exists")
            else:
                u = User(email=email_new, hashed_password=pwd_context.hash(pw_new), role=role_new, full_name=full_name)
                db.add(u); db.commit(); db.refresh(u)
                if role_new == "patient":
                    p = PatientProfile(user_id=u.id, demographics={}, medical_history="")
                    db.add(p); db.commit()
                st.success(f"Created {role_new}: {email_new}")

    st.markdown("---")
    st.markdown("### System Info")
    st.code(f"DB = {os.getenv('DATABASE_URL', 'sqlite:///./data/app.db')}")
    db.close()
