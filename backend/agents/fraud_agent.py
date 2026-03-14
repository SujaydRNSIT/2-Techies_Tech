"""
FraudAgent - Combines all signals to calculate fraud risk score
"""
from typing import Dict, Any
from agents.base_agent import BaseAgent

class FraudAgent(BaseAgent):
    """
    Central fraud detection agent that combines all signals
    from other agents to calculate final fraud risk score.
    """
    
    # Scoring rules
    SCORING_RULES = {
        "ai_image_suspicion": 40,
        "image_reused_online": 30,
        "suspicious_url": 20,
        "unverified_merchant": 20,
        "fraud_case_similarity": 20,
        "security_threat": 25,
        "metadata_anomaly": 15,
        "manipulation_detected": 35
    }
    
    def __init__(self, event_logger=None):
        super().__init__("FraudAgent", event_logger)
    
    def calculate_fraud_score(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate fraud score based on all signals
        """
        score = 0
        breakdown = {}
        risk_factors = []
        
        # EvidenceAgent signals
        evidence = signals.get("evidence", {})
        ai_analysis = evidence.get("ai_analysis", {})
        
        if ai_analysis.get("ai_generated_probability", 0) > 50:
            score += self.SCORING_RULES["ai_image_suspicion"]
            breakdown["ai_generated_image"] = self.SCORING_RULES["ai_image_suspicion"]
            risk_factors.append("AI-generated image detected")
        
        if ai_analysis.get("manipulation_detected", False):
            score += self.SCORING_RULES["manipulation_detected"]
            breakdown["image_manipulation"] = self.SCORING_RULES["manipulation_detected"]
            risk_factors.append("Image manipulation detected")
        
        # Image reuse detection
        image_reuse = signals.get("image_reuse", {})
        if image_reuse.get("found_online", False):
            score += self.SCORING_RULES["image_reused_online"]
            breakdown["image_reuse"] = self.SCORING_RULES["image_reused_online"]
            risk_factors.append("Image found online (possible reuse)")
        
        # Metadata anomalies
        metadata = evidence.get("metadata", {})
        if metadata.get("suspicious_compression", False):
            score += self.SCORING_RULES["metadata_anomaly"]
            breakdown["metadata_anomaly"] = self.SCORING_RULES["metadata_anomaly"]
            risk_factors.append("Suspicious image compression")
        
        # SecurityAgent signals
        security = signals.get("security", {})
        if not security.get("overall_safe", True):
            score += self.SCORING_RULES["security_threat"]
            breakdown["security_threat"] = self.SCORING_RULES["security_threat"]
            risk_factors.extend(security.get("threats_found", []))
        
        # Check for suspicious URLs
        url_scans = security.get("url_scans", [])
        for url_scan in url_scans:
            if not url_scan.get("safe", True):
                score += self.SCORING_RULES["suspicious_url"]
                breakdown["suspicious_url"] = self.SCORING_RULES["suspicious_url"]
                risk_factors.append(f"Suspicious URL: {url_scan.get('url', '')}")
                break  # Only count once
        
        # MerchantAgent signals
        merchant = signals.get("merchant", {})
        if not merchant.get("verified", True):
            score += self.SCORING_RULES["unverified_merchant"]
            breakdown["unverified_merchant"] = self.SCORING_RULES["unverified_merchant"]
            risk_factors.append("Unverified merchant")
        
        # KnowledgeAgent signals
        knowledge = signals.get("knowledge", {})
        if knowledge.get("pattern_detected", False):
            score += self.SCORING_RULES["fraud_case_similarity"]
            breakdown["fraud_pattern_match"] = self.SCORING_RULES["fraud_case_similarity"]
            risk_factors.append("Similar to known fraud patterns")
        
        # Cap score at 100
        score = min(score, 100)
        
        # Determine decision
        if score <= 30:
            decision = "approved"
            decision_reason = "Low fraud risk - automatic approval"
        elif score <= 70:
            decision = "manual_review"
            decision_reason = "Medium fraud risk - requires manual review"
        else:
            decision = "rejected"
            decision_reason = "High fraud risk - automatic rejection"
        
        return {
            "fraud_score": score,
            "breakdown": breakdown,
            "risk_factors": risk_factors,
            "decision": decision,
            "decision_reason": decision_reason
        }
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute fraud risk assessment
        
        Context must contain:
        - evidence: EvidenceAgent results
        - security: SecurityAgent results
        - merchant: MerchantAgent results
        - knowledge: KnowledgeAgent results
        - image_reuse: Image reuse detection results
        - claim_id: Unique claim identifier
        """
        claim_id = context.get("claim_id")
        self.start_task(claim_id)
        
        try:
            signals = {
                "evidence": context.get("evidence", {}),
                "security": context.get("security", {}),
                "merchant": context.get("merchant", {}),
                "knowledge": context.get("knowledge", {}),
                "image_reuse": context.get("image_reuse", {})
            }
            
            result = self.calculate_fraud_score(signals)
            
            self.log_event("fraud_score_calculated", {
                "fraud_score": result["fraud_score"],
                "decision": result["decision"],
                "risk_factors": len(result["risk_factors"])
            })
            
            self.complete_task(result)
            return result
            
        except Exception as e:
            error_result = {
                "fraud_score": 50,
                "decision": "manual_review",
                "decision_reason": f"Error in fraud assessment: {str(e)}",
                "error": str(e)
            }
            self.fail_task(str(e))
            return error_result
