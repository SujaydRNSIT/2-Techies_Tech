"""
KnowledgeAgent - Unsiloed AI style knowledge retrieval
Uses FAISS for similarity search of past fraud cases
"""
import os
import json
import pickle
import numpy as np
from typing import Dict, Any, List, Optional
import openai
from agents.base_agent import BaseAgent

class KnowledgeAgent(BaseAgent):
    """
    Knowledge retrieval agent for finding similar fraud patterns.
    Uses FAISS vector store with OpenAI embeddings.
    """
    
    def __init__(self, event_logger=None):
        super().__init__("KnowledgeAgent", event_logger)
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.fraud_cases = []
        self.embeddings = []
        self.load_knowledge_base()
    
    def load_knowledge_base(self):
        """Load or initialize the fraud case knowledge base"""
        kb_path = "./knowledge_base.pkl"
        
        if os.path.exists(kb_path):
            try:
                with open(kb_path, 'rb') as f:
                    data = pickle.load(f)
                    self.fraud_cases = data.get("cases", [])
                    self.embeddings = data.get("embeddings", [])
            except:
                self._init_default_cases()
        else:
            self._init_default_cases()
    
    def _init_default_cases(self):
        """Initialize with default fraud case examples"""
        default_cases = [
            {
                "case_id": "FRAUD_001",
                "description": "Customer submitted AI-generated image of damaged product. Image showed inconsistent lighting and unnatural texture patterns.",
                "fraud_indicators": ["ai_generated_image", "inconsistent_lighting", "unnatural_texture"],
                "fraud_score": 85,
                "outcome": "rejected"
            },
            {
                "case_id": "FRAUD_002",
                "description": "Same damage image used for multiple refund claims across different accounts. Reverse image search found duplicates.",
                "fraud_indicators": ["image_reuse", "multiple_accounts", "coordinated_fraud"],
                "fraud_score": 95,
                "outcome": "rejected"
            },
            {
                "case_id": "FRAUD_003",
                "description": "Claim from unverified merchant with suspicious URL patterns. URL contained credential harvesting keywords.",
                "fraud_indicators": ["unverified_merchant", "suspicious_url", "phishing_attempt"],
                "fraud_score": 75,
                "outcome": "rejected"
            },
            {
                "case_id": "LEGIT_001",
                "description": "Clear damage visible on authentic product. Consistent lighting, natural wear patterns, verified merchant.",
                "fraud_indicators": [],
                "fraud_score": 10,
                "outcome": "approved"
            },
            {
                "case_id": "LEGIT_002",
                "description": "Minor product defect with genuine photo. Customer history shows legitimate purchases, no red flags.",
                "fraud_indicators": [],
                "fraud_score": 15,
                "outcome": "approved"
            },
            {
                "case_id": "FRAUD_004",
                "description": "Photoshopped damage - shadows inconsistent with light source. Evidence of digital manipulation detected.",
                "fraud_indicators": ["photoshop_manipulation", "shadow_inconsistency", "digital_artifacts"],
                "fraud_score": 90,
                "outcome": "rejected"
            },
            {
                "case_id": "FRAUD_005",
                "description": "New account with first order claiming high-value item damage. No purchase history, disposable email domain.",
                "fraud_indicators": ["new_account", "high_value_claim", "disposable_email"],
                "fraud_score": 70,
                "outcome": "manual_review"
            },
            {
                "case_id": "FRAUD_006",
                "description": "Stock image from internet used as damage evidence. Reverse search found original unaltered image.",
                "fraud_indicators": ["stock_image", "image_reuse", "false_evidence"],
                "fraud_score": 92,
                "outcome": "rejected"
            }
        ]
        
        self.fraud_cases = default_cases
        # Generate embeddings for default cases
        self._generate_embeddings()
        self.save_knowledge_base()
    
    def _generate_embeddings(self):
        """Generate embeddings for all cases using OpenAI"""
        try:
            texts = [case["description"] for case in self.fraud_cases]
            response = self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=texts
            )
            self.embeddings = [item.embedding for item in response.data]
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            # Fallback to random embeddings for demo
            self.embeddings = [np.random.randn(1536).tolist() for _ in self.fraud_cases]
    
    def save_knowledge_base(self):
        """Save knowledge base to disk"""
        kb_path = "./knowledge_base.pkl"
        with open(kb_path, 'wb') as f:
            pickle.dump({
                "cases": self.fraud_cases,
                "embeddings": self.embeddings
            }, f)
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for a text"""
        try:
            response = self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error getting embedding: {e}")
            # Return zero vector as fallback
            return [0.0] * 1536
    
    def cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        a = np.array(a)
        b = np.array(b)
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def search_similar_cases(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search for similar fraud cases"""
        if not self.embeddings:
            return []
        
        query_embedding = self.get_embedding(query)
        
        # Calculate similarities
        similarities = []
        for i, case_embedding in enumerate(self.embeddings):
            sim = self.cosine_similarity(query_embedding, case_embedding)
            similarities.append((i, sim))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top k results
        results = []
        for idx, sim in similarities[:top_k]:
            case = self.fraud_cases[idx].copy()
            case["similarity_score"] = round(sim * 100, 2)
            results.append(case)
        
        return results
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute knowledge retrieval
        
        Context must contain:
        - claim_description: Description of the current claim
        - evidence_summary: Summary of evidence findings
        - claim_id: Unique claim identifier
        """
        claim_description = context.get("claim_description", "")
        evidence_summary = context.get("evidence_summary", "")
        claim_id = context.get("claim_id")
        
        self.start_task(claim_id)
        
        try:
            # Create search query
            search_query = f"{claim_description} {evidence_summary}"
            
            # Search for similar cases
            similar_cases = self.search_similar_cases(search_query)
            
            # Calculate fraud signal based on similar cases
            fraud_signal = 0
            avg_similar_fraud_score = 0
            
            if similar_cases:
                # Weight by similarity
                weighted_scores = []
                for case in similar_cases:
                    weight = case["similarity_score"] / 100
                    weighted_scores.append(case["fraud_score"] * weight)
                
                avg_similar_fraud_score = sum(weighted_scores) / sum(
                    case["similarity_score"] / 100 for case in similar_cases
                )
                
                # If similar cases had high fraud scores, increase signal
                if avg_similar_fraud_score > 50:
                    fraud_signal = min(20 * (avg_similar_fraud_score / 50), 20)
            
            result = {
                "similar_cases": similar_cases,
                "similarity_scores": [case["similarity_score"] for case in similar_cases],
                "avg_historical_fraud_score": round(avg_similar_fraud_score, 2),
                "fraud_signal": round(fraud_signal, 2),
                "pattern_detected": any(case["similarity_score"] > 80 for case in similar_cases)
            }
            
            self.log_event("knowledge_retrieval_complete", {
                "similar_cases_found": len(similar_cases),
                "pattern_detected": result["pattern_detected"]
            })
            
            self.complete_task(result)
            return result
            
        except Exception as e:
            error_result = {
                "similar_cases": [],
                "fraud_signal": 10,
                "error": str(e)
            }
            self.fail_task(str(e))
            return error_result
    
    def add_case(self, case: Dict[str, Any]):
        """Add a new case to the knowledge base"""
        self.fraud_cases.append(case)
        # Generate embedding for new case
        embedding = self.get_embedding(case["description"])
        self.embeddings.append(embedding)
        self.save_knowledge_base()
