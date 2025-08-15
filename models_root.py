from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


# ===================== USER =====================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # patient, clinician, admin
    full_name = Column(String)
    is_active = Column(Boolean, default=True)

    # Relationships
    patient_profile = relationship("PatientProfile", back_populates="user", uselist=False)
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")


# ===================== PATIENT PROFILE =====================
class PatientProfile(Base):
    __tablename__ = "patient_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    demographics = Column(JSON, default={})
    medical_history = Column(String)

    # Relationships
    user = relationship("User", back_populates="patient_profile")
    sensor_streams = relationship("SensorStream", back_populates="patient", cascade="all, delete-orphan")


# ===================== SENSOR STREAM =====================
class SensorStream(Base):
    __tablename__ = "sensor_streams"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id"), nullable=False)
    sensor_type = Column(String, nullable=False)  # e.g., imu, emg, patient_report
    payload = Column(JSON, default={})
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    patient = relationship("PatientProfile", back_populates="sensor_streams")


# ===================== PREDICTIONS =====================
class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id"), nullable=False)
    scenario = Column(JSON, default={})
    result = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)


# ===================== AUDIT LOG =====================
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)
    details = Column(JSON, default={})
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="audit_logs")
