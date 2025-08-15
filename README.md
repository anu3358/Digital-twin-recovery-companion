# Digital-Twin Recovery Companion 🩺🤖

An **AI-powered virtual recovery companion** that predicts patient recovery, optimizes therapy plans, and bridges the gap between clinicians and patients in real-time.

🚀 **Hackathon Use Case:** Helping restorative healthcare patients get *faster, personalized recovery* while giving clinicians predictive insights.

---

## 📌 Features
- **Role-based dashboards** for Patients, Clinicians, and Admins
- **AI-powered "What-if" simulator** using PyTorch
- **Wearable sensor data ingestion** (IMU, EMG, vitals)
- **3D Digital Twin Visualization**
- **Audit logging** for compliance
- **Instant PDF recovery reports**
- **Pre-filled demo dataset** for live judging

---

## 📂 Folder Structure
```
app.py                  # Streamlit main app
database.py             # SQLAlchemy DB setup
models.py               # ORM models
models/torch_model.py   # Example PyTorch model
demo_data/              # Pre-filled demo patients, sensors, predictions
sample_data/            # Wearable CSV example
```

---

## 🧪 Local Setup
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python demo_data/load_demo_data.py  # Load demo patients
streamlit run app.py
```

**Demo accounts:**
```
Patient:   patient1@example.com / changeme
Clinician: clinician1@example.com / changeme
Admin:     admin@dtc.local      / changeme
```

---

## ☁️ Deploy to Streamlit Cloud
1. Push this repo to GitHub.
2. Go to [Streamlit Cloud](https://share.streamlit.io/) → New App → Select your repo.
3. Set `Main file path` to `app.py`.
4. Add environment variables in Secrets (if using Postgres).

---

## 🎯 Hackathon Judge Demo Flow
1. **Login as Clinician** → view populated dashboards.
2. **Data Ingestion** → upload `sample_data/wearable_demo.csv` → run prediction.
3. **Patient Dashboard** → adjust sliders to see live prediction changes.
4. **Generate PDF report** for a patient and share.

---
© 2025 Digital-Twin Recovery Companion
