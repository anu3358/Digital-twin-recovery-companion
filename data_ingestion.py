import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from models import SensorStream
from datetime import datetime

EXPECTED_COLS = ["timestamp","accel_x","accel_y","accel_z","emg","spo2","hr","step_count"]

def parse_and_store(csv_bytes: bytes, patient_id: int, db: Session):
    df = pd.read_csv(pd.io.common.BytesIO(csv_bytes))
    # basic normalization
    cols = [c.strip().lower() for c in df.columns]
    df.columns = cols
    missing = [c for c in EXPECTED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}. Expected {EXPECTED_COLS}")

    # store raw rows as sensor_stream entries (chunked for speed)
    preview_rows = 0
    for _, row in df.iterrows():
        payload = {
            "accel": [float(row["accel_x"]), float(row["accel_y"]), float(row["accel_z"])],
            "emg": float(row["emg"]),
            "spo2": float(row["spo2"]),
            "hr": float(row["hr"]),
            "step_count": float(row["step_count"]),
        }
        ts = None
        try:
            ts = pd.to_datetime(row["timestamp"]).to_pydatetime()
        except Exception:
            ts = datetime.utcnow()
        s = SensorStream(patient_id=patient_id, timestamp=ts, sensor_type="wearable_csv", payload=payload)
        db.add(s)
        preview_rows += 1
        if preview_rows >= 2000:  # avoid giant inserts on demo
            break
    db.commit()

    # feature engineering
    acc_mag = np.sqrt(df["accel_x"]**2 + df["accel_y"]**2 + df["accel_z"]**2)
    emg_rms = np.sqrt(np.mean(np.square(df["emg"])))
    cadence_est = (df["step_count"].diff().clip(lower=0).fillna(0).mean()) * 60  # steps/min
    feats = {
        "acc_mag_mean": float(acc_mag.mean()),
        "acc_mag_std": float(acc_mag.std()),
        "emg_rms": float(emg_rms),
        "hr_mean": float(df["hr"].mean()),
        "spo2_mean": float(df["spo2"].mean()),
        "cadence_est": float(cadence_est),
    }
    return df.head(10), feats
