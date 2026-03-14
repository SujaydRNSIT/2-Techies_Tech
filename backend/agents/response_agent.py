"""
ResponseAgent - Concierge-style automated response generation
"""
import os
from typing import Dict, Any
import openai
from agents.base_agent import BaseAgent

class ResponseAgent(BaseAgent):
    """
    Generates automated email responses for customers
    based on refund decision outcomes.
    """
    
    def __init__(self, event_logger=None):
        super().__init__("ResponseAgent", event_logger)
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def generate_approved_response(self, context: Dict[str, Any]) -> str:
        """Generate response for approved refund"""
        refund_id = context.get("refund_id", "")
        amount = context.get("refund_amount", 0)
        
        return f"""Dear Valued Customer,

Great news! Your refund claim has been approved after automated verification.

Refund Details:
- Refund ID: {refund_id}
- Amount: ₹{amount:,.2f}
- Status: Processing

Your refund is being processed and should appear in your original payment method within 5-7 business days.

If you have any questions, please contact our support team.

Thank you for your patience.

Best regards,
RefundShield AI Team"""
    
    def generate_rejected_response(self, context: Dict[str, Any]) -> str:
        """Generate response for rejected refund"""
        fraud_score = context.get("fraud_score", 0)
        risk_factors = context.get("risk_factors", [])
        
        reason = ""
        if "Image found online" in str(risk_factors):
            reason = "the submitted evidence appears to be reused from online sources"
        elif "AI-generated" in str(risk_factors):
            reason = "the submitted image shows signs of AI generation or manipulation"
        elif "suspicious" in str(risk_factors).lower():
            reason = "potential security concerns were identified"
        else:
            reason = "our fraud detection systems identified suspicious patterns"
        
        return f"""Dear Customer,

We regret to inform you that your refund request has been rejected.

Reason: After careful investigation, {reason}.

Fraud Risk Score: {fraud_score}/100

If you believe this decision was made in error, you may:
1. Submit additional documentation supporting your claim
2. Request a manual review by our support team
3. Contact us within 7 days to appeal this decision

Please note that submitting fraudulent claims may result in account suspension.

Best regards,
RefundShield AI Team"""
    
    def generate_manual_review_response(self, context: Dict[str, Any]) -> str:
        """Generate response for manual review"""
        return f"""Dear Customer,

Your refund claim (ID: {context.get('claim_id')}) has been flagged for manual review by our specialist team.

This is a standard procedure for claims that require additional verification. Your case is being reviewed and you will receive an update within 24-48 hours.

No further action is required from you at this time.

Thank you for your patience.

Best regards,
RefundShield AI Team"""
    
    async def generate_ai_response(self, context: Dict[str, Any]) -> str:
        """Generate AI-powered personalized response"""
        try:
            decision = context.get("decision", "manual_review")
            fraud_score = context.get("fraud_score", 0)
            claim_reason = context.get("claim_reason", "")
            
            prompt = f"""Generate a professional customer service email response for a refund claim.

Decision: {decision}
Fraud Score: {fraud_score}/100
Claim Reason: {claim_reason}

The tone should be {'congratulatory but professional' if decision == 'approved' else 'firm but respectful' if decision == 'rejected' else 'reassuring and professional'}.

Keep it concise (under 200 words) and include relevant details.
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            # Fallback to template
            return self.generate_template_response(context)
    
    def generate_template_response(self, context: Dict[str, Any]) -> str:
        """Generate response using templates"""
        decision = context.get("decision", "manual_review")
        
        if decision == "approved":
            return self.generate_approved_response(context)
        elif decision == "rejected":
            return self.generate_rejected_response(context)
        else:
            return self.generate_manual_review_response(context)
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute response generation
        
        Context must contain:
        - decision: approved/rejected/manual_review
        - claim_id: Unique claim identifier
        - refund_id: Refund ID (if approved)
        - refund_amount: Amount
        - fraud_score: Fraud score
        - risk_factors: List of risk factors
        - use_ai: Whether to use AI generation
        """
        claim_id = context.get("claim_id")
        use_ai = context.get("use_ai", True)
        
        self.start_task(claim_id)
        
        try:
            if use_ai:
                message = await self.generate_ai_response(context)
            else:
                message = self.generate_template_response(context)
            
            result = {
                "message": message,
                "decision": context.get("decision"),
                "delivery_method": "email",
                "personalized": use_ai
            }
            
            self.log_event("response_generated", {
                "decision": context.get("decision"),
                "personalized": use_ai
            })
            
            self.complete_task(result)
            return result
            
        except Exception as e:
            # Fallback to template on error
            message = self.generate_template_response(context)
            result = {
                "message": message,
                "decision": context.get("decision"),
                "fallback": True
            }
            self.fail_task(str(e))
            return result
