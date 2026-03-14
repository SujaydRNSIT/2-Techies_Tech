"""
Database models for RefundShield AI
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

Base = declarative_base()

class RefundClaim(Base):
    """Stores refund claim investigations"""
    __tablename__ = "refund_claims"
    
    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(String(100), unique=True, index=True)
    order_id = Column(String(100), index=True)
    payment_id = Column(String(100))
    merchant_name = Column(String(255))
    refund_amount = Column(Float)
    claim_reason = Column(Text)
    
    # Evidence analysis
    evidence_image_path = Column(String(500))
    image_metadata = Column(JSON)
    image_perceptual_hash = Column(String(100))
    
    # Agent results
    evidence_analysis = Column(JSON)
    security_scan = Column(JSON)
    merchant_verification = Column(JSON)
    fraud_score = Column(Integer, default=0)
    
    # Decision
    decision = Column(String(50))  # approved, rejected, manual_review
    refund_id = Column(String(100))
    refund_status = Column(String(50))
    
    # Report
    investigation_report = Column(JSON)
    customer_response = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class EventLog(Base):
    """S2.dev style event streaming logs"""
    __tablename__ = "event_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(100), unique=True, index=True)
    event_type = Column(String(100), index=True)
    claim_id = Column(String(100), index=True)
    agent_name = Column(String(100))
    event_data = Column(JSON)
    severity = Column(String(50), default="info")  # info, warning, error, critical
    timestamp = Column(DateTime, default=datetime.utcnow)
    source = Column(String(100), default="refundshield")

class FraudCase(Base):
    """Knowledge base for fraud patterns"""
    __tablename__ = "fraud_cases"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(String(100), unique=True, index=True)
    case_type = Column(String(100))
    description = Column(Text)
    fraud_indicators = Column(JSON)
    fraud_score_range = Column(String(50))
    vector_embedding = Column(Text)  # Serialized vector for FAISS
    created_at = Column(DateTime, default=datetime.utcnow)

# Database setup
DATABASE_URL = "sqlite:///./refundshield.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
