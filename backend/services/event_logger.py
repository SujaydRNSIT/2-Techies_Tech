"""
S2.dev style event streaming service
"""
import uuid
import json
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from database.models import EventLog

class EventLogger:
    """Simulates S2.dev event streaming for observability"""
    
    EVENT_TYPES = {
        "claim_received": "New refund claim submitted",
        "agent_started": "Agent started processing",
        "agent_completed": "Agent completed task",
        "image_analyzed": "Image analysis completed",
        "security_scan_complete": "Security scan finished",
        "merchant_verified": "Merchant verification completed",
        "fraud_score_calculated": "Fraud risk score computed",
        "refund_processed": "Refund payment processed",
        "refund_rejected": "Refund claim rejected",
        "report_generated": "Investigation report created",
        "response_sent": "Customer notification sent",
        "error": "System error occurred"
    }
    
    def __init__(self, db: Optional[Session] = None):
        self.db = db
        self.events_buffer = []
    
    def log_event(
        self,
        event_type: str,
        claim_id: str,
        agent_name: Optional[str] = None,
        event_data: Optional[Dict[str, Any]] = None,
        severity: str = "info"
    ) -> Dict[str, Any]:
        """Log an event to the event stream"""
        
        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "claim_id": claim_id,
            "agent_name": agent_name,
            "event_data": event_data or {},
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "refundshield.ai",
            "description": self.EVENT_TYPES.get(event_type, "Unknown event")
        }
        
        # Store in database if available
        if self.db:
            db_event = EventLog(
                event_id=event["event_id"],
                event_type=event_type,
                claim_id=claim_id,
                agent_name=agent_name,
                event_data=event_data,
                severity=severity,
                source=event["source"]
            )
            self.db.add(db_event)
            self.db.commit()
        
        # Also buffer for real-time streaming simulation
        self.events_buffer.append(event)
        
        # Print for debugging
        print(f"[S2.EVENT] {event_type} | Claim: {claim_id} | Agent: {agent_name} | Severity: {severity}")
        
        return event
    
    def get_events(
        self,
        claim_id: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 100
    ) -> list:
        """Retrieve events from the stream"""
        if self.db:
            query = self.db.query(EventLog)
            
            if claim_id:
                query = query.filter(EventLog.claim_id == claim_id)
            if event_type:
                query = query.filter(EventLog.event_type == event_type)
            
            return query.order_by(EventLog.timestamp.desc()).limit(limit).all()
        
        # Return from buffer if no DB
        events = self.events_buffer
        if claim_id:
            events = [e for e in events if e["claim_id"] == claim_id]
        if event_type:
            events = [e for e in events if e["event_type"] == event_type]
        
        return events[-limit:]
    
    def stream_events(self, claim_id: Optional[str] = None):
        """Simulate real-time event streaming"""
        events = self.get_events(claim_id=claim_id)
        for event in events:
            yield f"data: {json.dumps(event)}\n\n"

# Global event logger instance
event_logger = EventLogger()
