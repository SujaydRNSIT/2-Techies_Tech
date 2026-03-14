"""
RefundAgent - Executes refunds via Razorpay API
"""
import os
from typing import Dict, Any
import razorpay
from agents.base_agent import BaseAgent

class RefundAgent(BaseAgent):
    """
    Refund execution agent using Razorpay API.
    Processes refunds based on fraud score decision.
    """
    
    def __init__(self, event_logger=None):
        super().__init__("RefundAgent", event_logger)
        self.key_id = os.getenv("RAZORPAY_KEY_ID")
        self.key_secret = os.getenv("RAZORPAY_KEY_SECRET")
        
        if self.key_id and self.key_secret:
            self.client = razorpay.Client(auth=(self.key_id, self.key_secret))
        else:
            self.client = None
    
    async def execute_refund(
        self,
        payment_id: str,
        amount: float,
        notes: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Execute refund via Razorpay API
        """
        if not self.client:
            # Simulate refund for demo
            return self._simulate_refund(payment_id, amount, notes)
        
        try:
            # Razorpay expects amount in smallest currency unit (paise for INR)
            amount_paise = int(amount * 100)
            
            refund_data = {
                "amount": amount_paise,
                "speed": "optimum",  # Try for instant refund
                "notes": notes or {}
            }
            
            refund = self.client.payment.refund(payment_id, refund_data)
            
            return {
                "success": True,
                "refund_id": refund.get("id"),
                "payment_id": refund.get("payment_id"),
                "amount": refund.get("amount", 0) / 100,  # Convert back to rupees
                "status": refund.get("status"),
                "speed_processed": refund.get("speed_processed"),
                "created_at": refund.get("created_at"),
                "source": "razorpay_live"
            }
            
        except razorpay.errors.BadRequestError as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "bad_request"
            }
        except razorpay.errors.GatewayError as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "gateway_error"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "unknown"
            }
    
    def _simulate_refund(self, payment_id: str, amount: float, notes: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate refund for demo without actual API"""
        import uuid
        from datetime import datetime
        
        return {
            "success": True,
            "refund_id": f"rfnd_{uuid.uuid4().hex[:12]}",
            "payment_id": payment_id,
            "amount": amount,
            "status": "processed",
            "speed_processed": "optimum",
            "created_at": int(datetime.now().timestamp()),
            "source": "razorpay_simulated",
            "note": "This is a simulated refund (Razorpay API keys not configured)"
        }
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute refund processing
        
        Context must contain:
        - payment_id: Razorpay payment ID
        - refund_amount: Amount to refund
        - fraud_score: Calculated fraud score
        - decision: Decision (approved/rejected/manual_review)
        - claim_id: Unique claim identifier
        - claim_reason: Reason for refund
        - order_id: Order ID
        """
        payment_id = context.get("payment_id")
        refund_amount = context.get("refund_amount", 0)
        fraud_score = context.get("fraud_score", 0)
        decision = context.get("decision", "manual_review")
        claim_id = context.get("claim_id")
        claim_reason = context.get("claim_reason", "")
        order_id = context.get("order_id", "")
        
        self.start_task(claim_id)
        
        try:
            # Only process refund if decision is approved
            if decision == "approved":
                notes = {
                    "claim_id": claim_id,
                    "order_id": order_id,
                    "reason": claim_reason,
                    "fraud_score": str(fraud_score)
                }
                
                result = await self.execute_refund(payment_id, refund_amount, notes)
                
                if result.get("success"):
                    self.log_event("refund_processed", {
                        "refund_id": result.get("refund_id"),
                        "amount": refund_amount,
                        "status": result.get("status")
                    })
                else:
                    self.log_event("error", {
                        "error": result.get("error"),
                        "stage": "refund_processing"
                    }, severity="error")
                
                self.complete_task(result)
                return result
                
            elif decision == "rejected":
                result = {
                    "success": False,
                    "rejected": True,
                    "reason": "Refund rejected due to high fraud risk",
                    "fraud_score": fraud_score
                }
                
                self.log_event("refund_rejected", {
                    "fraud_score": fraud_score,
                    "reason": "High fraud risk"
                })
                
                self.complete_task(result)
                return result
                
            else:  # manual_review
                result = {
                    "success": False,
                    "pending_review": True,
                    "reason": "Refund pending manual review",
                    "fraud_score": fraud_score
                }
                
                self.log_event("refund_pending_review", {
                    "fraud_score": fraud_score
                })
                
                self.complete_task(result)
                return result
                
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e)
            }
            self.fail_task(str(e))
            return error_result
