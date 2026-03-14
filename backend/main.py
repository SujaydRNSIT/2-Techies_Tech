"""
RefundShield AI - Main FastAPI Application
Autonomous Refund Fraud Investigator
"""
import os
import uuid
import shutil
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database.models import init_db, get_db, RefundClaim
from services.event_logger import EventLogger, event_logger
from services.image_search import image_search_service

from agents import (
    EvidenceAgent,
    SecurityAgent,
    MerchantAgent,
    FraudAgent,
    RefundAgent,
    KnowledgeAgent,
    ReportAgent,
    ResponseAgent
)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize database on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="RefundShield AI",
    description="Autonomous Refund Fraud Investigator",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure upload directory exists
UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# ==================== Pydantic Models ====================

class ClaimResponse(BaseModel):
    claim_id: str
    fraud_score: int
    decision: str
    refund_status: str
    investigation_report: dict
    customer_response: str

class ClaimsListResponse(BaseModel):
    claims: list

class EventsResponse(BaseModel):
    events: list

# ==================== Helper Functions ====================

async def process_refund_claim(
    order_id: str,
    merchant_name: str,
    payment_id: str,
    refund_amount: float,
    claim_reason: str,
    image_path: Optional[str],
    db: Session
) -> dict:
    """
    Orchestrate all agents to process a refund claim
    Emergent AI style multi-agent coordination
    """
    claim_id = f"CLM_{uuid.uuid4().hex[:12].upper()}"
    
    # Initialize event logger with DB
    logger = EventLogger(db)
    
    # Log claim received
    logger.log_event("claim_received", claim_id, event_data={
        "order_id": order_id,
        "merchant": merchant_name,
        "amount": refund_amount
    })
    
    # ========== STEP 1: Evidence Analysis ==========
    evidence_agent = EvidenceAgent(logger)
    evidence_result = await evidence_agent.execute({
        "claim_id": claim_id,
        "image_path": image_path,
        "claim_reason": claim_reason
    })
    
    # ========== STEP 2: Reverse Image Search ==========
    image_reuse_result = {"found_online": False, "matches_count": 0, "source_urls": []}
    if image_path:
        image_reuse_result = image_search_service.search_local_image(image_path)
    
    # ========== STEP 3: Security Scan ==========
    security_agent = SecurityAgent(logger)
    security_result = await security_agent.execute({
        "claim_id": claim_id,
        "file_path": image_path,
        "claim_reason": claim_reason
    })
    
    # ========== STEP 4: Merchant Verification ==========
    merchant_agent = MerchantAgent(logger)
    merchant_result = await merchant_agent.execute({
        "claim_id": claim_id,
        "merchant_name": merchant_name
    })
    
    # ========== STEP 5: Knowledge Retrieval ==========
    knowledge_agent = KnowledgeAgent(logger)
    evidence_summary = evidence_result.get("summary", "")
    knowledge_result = await knowledge_agent.execute({
        "claim_id": claim_id,
        "claim_description": claim_reason,
        "evidence_summary": evidence_summary
    })
    
    # ========== STEP 6: Fraud Risk Assessment ==========
    fraud_agent = FraudAgent(logger)
    fraud_result = await fraud_agent.execute({
        "claim_id": claim_id,
        "evidence": evidence_result,
        "security": security_result,
        "merchant": merchant_result,
        "knowledge": knowledge_result,
        "image_reuse": image_reuse_result
    })
    
    # ========== STEP 7: Refund Processing ==========
    refund_agent = RefundAgent(logger)
    refund_result = await refund_agent.execute({
        "claim_id": claim_id,
        "order_id": order_id,
        "payment_id": payment_id,
        "refund_amount": refund_amount,
        "claim_reason": claim_reason,
        "fraud_score": fraud_result.get("fraud_score", 0),
        "decision": fraud_result.get("decision", "manual_review")
    })
    
    # ========== STEP 8: Report Generation ==========
    report_agent = ReportAgent(logger)
    report_result = await report_agent.execute({
        "claim_id": claim_id,
        "order_id": order_id,
        "payment_id": payment_id,
        "merchant_name": merchant_name,
        "refund_amount": refund_amount,
        "claim_reason": claim_reason,
        "evidence": evidence_result,
        "security": security_result,
        "merchant": merchant_result,
        "knowledge": knowledge_result,
        "image_reuse": image_reuse_result,
        "fraud": fraud_result,
        "refund": refund_result
    })
    
    # ========== STEP 9: Response Generation ==========
    response_agent = ResponseAgent(logger)
    response_result = await response_agent.execute({
        "claim_id": claim_id,
        "decision": fraud_result.get("decision"),
        "refund_id": refund_result.get("refund_id"),
        "refund_amount": refund_amount,
        "fraud_score": fraud_result.get("fraud_score"),
        "risk_factors": fraud_result.get("risk_factors", []),
        "claim_reason": claim_reason,
        "use_ai": True
    })
    
    # ========== Save to Database ==========
    db_claim = RefundClaim(
        claim_id=claim_id,
        order_id=order_id,
        payment_id=payment_id,
        merchant_name=merchant_name,
        refund_amount=refund_amount,
        claim_reason=claim_reason,
        evidence_image_path=image_path,
        image_metadata=evidence_result.get("metadata"),
        image_perceptual_hash=evidence_result.get("perceptual_hash", {}).get("phash"),
        evidence_analysis=evidence_result,
        security_scan=security_result,
        merchant_verification=merchant_result,
        fraud_score=fraud_result.get("fraud_score", 0),
        decision=fraud_result.get("decision"),
        refund_id=refund_result.get("refund_id"),
        refund_status=refund_result.get("status", "failed"),
        investigation_report=report_result,
        customer_response=response_result.get("message", "")
    )
    
    db.add(db_claim)
    db.commit()
    db.refresh(db_claim)
    
    return {
        "claim_id": claim_id,
        "fraud_score": fraud_result.get("fraud_score", 0),
        "decision": fraud_result.get("decision"),
        "decision_reason": fraud_result.get("decision_reason"),
        "refund_status": refund_result.get("status", "failed"),
        "refund_id": refund_result.get("refund_id"),
        "investigation_report": report_result,
        "customer_response": response_result.get("message"),
        "risk_factors": fraud_result.get("risk_factors", [])
    }

# ==================== API Endpoints ====================

@app.post("/submit-claim", response_model=ClaimResponse)
async def submit_claim(
    order_id: str = Form(...),
    merchant_name: str = Form(...),
    payment_id: str = Form(...),
    refund_amount: float = Form(...),
    claim_reason: str = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Submit a refund claim for AI investigation
    """
    image_path = None
    
    try:
        # Save uploaded image
        if image:
            file_extension = Path(image.filename).suffix
            unique_filename = f"{uuid.uuid4().hex}{file_extension}"
            image_path = UPLOAD_DIR / unique_filename
            
            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
        
        # Process the claim
        result = await process_refund_claim(
            order_id=order_id,
            merchant_name=merchant_name,
            payment_id=payment_id,
            refund_amount=refund_amount,
            claim_reason=claim_reason,
            image_path=str(image_path) if image_path else None,
            db=db
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if image:
            image.file.close()

@app.get("/claims", response_model=ClaimsListResponse)
async def get_claims(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get all refund claims
    """
    claims = db.query(RefundClaim).order_by(RefundClaim.created_at.desc()).limit(limit).all()
    
    return {
        "claims": [
            {
                "claim_id": c.claim_id,
                "order_id": c.order_id,
                "merchant_name": c.merchant_name,
                "refund_amount": c.refund_amount,
                "fraud_score": c.fraud_score,
                "decision": c.decision,
                "refund_status": c.refund_status,
                "created_at": c.created_at.isoformat() if c.created_at else None
            }
            for c in claims
        ]
    }

@app.get("/claims/{claim_id}")
async def get_claim(
    claim_id: str,
    db: Session = Depends(get_db)
):
    """
    Get specific claim details
    """
    claim = db.query(RefundClaim).filter(RefundClaim.claim_id == claim_id).first()
    
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    return {
        "claim_id": claim.claim_id,
        "order_id": claim.order_id,
        "merchant_name": claim.merchant_name,
        "refund_amount": claim.refund_amount,
        "claim_reason": claim.claim_reason,
        "fraud_score": claim.fraud_score,
        "decision": claim.decision,
        "refund_id": claim.refund_id,
        "refund_status": claim.refund_status,
        "investigation_report": claim.investigation_report,
        "customer_response": claim.customer_response,
        "created_at": claim.created_at.isoformat() if claim.created_at else None
    }

@app.get("/events", response_model=EventsResponse)
async def get_events(
    claim_id: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get event logs (S2.dev style event streaming)
    """
    from database.models import EventLog
    
    query = db.query(EventLog)
    
    if claim_id:
        query = query.filter(EventLog.claim_id == claim_id)
    if event_type:
        query = query.filter(EventLog.event_type == event_type)
    
    events = query.order_by(EventLog.timestamp.desc()).limit(limit).all()
    
    return {
        "events": [
            {
                "event_id": e.event_id,
                "event_type": e.event_type,
                "claim_id": e.claim_id,
                "agent_name": e.agent_name,
                "event_data": e.event_data,
                "severity": e.severity,
                "timestamp": e.timestamp.isoformat() if e.timestamp else None,
                "source": e.source
            }
            for e in events
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "RefundShield AI",
        "version": "1.0.0",
        "agents": [
            "EvidenceAgent",
            "SecurityAgent",
            "MerchantAgent",
            "FraudAgent",
            "RefundAgent",
            "KnowledgeAgent",
            "ReportAgent",
            "ResponseAgent"
        ]
    }

@app.get("/sponsor-status")
async def sponsor_status():
    """Check sponsor API integration status"""
    return {
        "integrations": {
            "razorpay": {
                "configured": bool(os.getenv("RAZORPAY_KEY_ID")),
                "name": "Razorpay",
                "purpose": "Payment refund execution"
            },
            "safedep": {
                "configured": bool(os.getenv("SAFEDEP_API_KEY")),
                "name": "SafeDep",
                "purpose": "File security scanning"
            },
            "gearsec": {
                "configured": bool(os.getenv("GEARSEC_API_KEY")),
                "name": "Gearsec",
                "purpose": "URL threat detection"
            },
            "crustdata": {
                "configured": bool(os.getenv("CRUSTDATA_API_KEY")),
                "name": "Crustdata",
                "purpose": "Company verification"
            },
            "virustotal": {
                "configured": bool(os.getenv("VIRUSTOTAL_API_KEY")),
                "name": "VirusTotal",
                "purpose": "URL reputation checking"
            },
            "serpapi": {
                "configured": bool(os.getenv("SERPAPI_API_KEY")),
                "name": "SerpAPI",
                "purpose": "Reverse image search"
            },
            "openai": {
                "configured": bool(os.getenv("OPENAI_API_KEY")),
                "name": "OpenAI",
                "purpose": "AI image analysis & response generation"
            },
            "s2dev": {
                "configured": True,
                "name": "S2.dev",
                "purpose": "Event streaming (simulated)"
            },
            "emergent": {
                "configured": True,
                "name": "Emergent AI",
                "purpose": "Multi-agent orchestration (simulated)"
            },
            "unsiloed": {
                "configured": True,
                "name": "Unsiloed AI",
                "purpose": "Knowledge retrieval (FAISS-based)"
            },
            "concierge": {
                "configured": True,
                "name": "Concierge",
                "purpose": "Response automation (OpenAI-powered)"
            }
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
