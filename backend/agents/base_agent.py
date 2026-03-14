"""
Base Agent class - Emergent AI style multi-agent orchestration
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

class BaseAgent(ABC):
    """Base class for all RefundShield AI agents"""
    
    def __init__(self, agent_name: str, event_logger=None):
        self.agent_name = agent_name
        self.agent_id = str(uuid.uuid4())
        self.event_logger = event_logger
        self.status = "idle"
        self.current_claim_id = None
    
    def log_event(self, event_type: str, data: Optional[Dict[str, Any]] = None, severity: str = "info"):
        """Log agent activity to event stream"""
        if self.event_logger:
            self.event_logger.log_event(
                event_type=event_type,
                claim_id=self.current_claim_id or "unknown",
                agent_name=self.agent_name,
                event_data=data,
                severity=severity
            )
    
    def start_task(self, claim_id: str):
        """Mark agent as starting a task"""
        self.current_claim_id = claim_id
        self.status = "running"
        self.log_event("agent_started", {"agent_id": self.agent_id})
    
    def complete_task(self, result: Dict[str, Any]):
        """Mark agent as completing a task"""
        self.status = "completed"
        self.log_event("agent_completed", {"result": result})
        self.current_claim_id = None
    
    def fail_task(self, error: str):
        """Mark agent as failing a task"""
        self.status = "failed"
        self.log_event("error", {"error": error}, severity="error")
        self.current_claim_id = None
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's primary task"""
        pass
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent metadata"""
        return {
            "agent_name": self.agent_name,
            "agent_id": self.agent_id,
            "status": self.status,
            "current_claim_id": self.current_claim_id,
            "timestamp": datetime.utcnow().isoformat()
        }
