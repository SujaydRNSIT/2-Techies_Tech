"""
EvidenceAgent - Analyzes refund evidence images using OpenAI Vision
"""
import os
import base64
import json
from typing import Dict, Any
from PIL import Image, ExifTags
import imagehash
from io import BytesIO
import openai
from agents.base_agent import BaseAgent

class EvidenceAgent(BaseAgent):
    """
    Agent responsible for analyzing refund evidence images.
    Uses OpenAI GPT-4 Vision API for image analysis.
    """
    
    def __init__(self, event_logger=None):
        super().__init__("EvidenceAgent", event_logger)
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def extract_metadata(self, image_path: str) -> Dict[str, Any]:
        """Extract image metadata using Pillow"""
        try:
            with Image.open(image_path) as img:
                metadata = {
                    "format": img.format,
                    "mode": img.mode,
                    "width": img.width,
                    "height": img.height,
                    "size_bytes": os.path.getsize(image_path),
                }
                
                # Extract EXIF data if available
                exif_data = {}
                if hasattr(img, '_getexif') and img._getexif():
                    exif = img._getexif()
                    for tag_id, value in exif.items():
                        tag = ExifTags.TAGS.get(tag_id, tag_id)
                        exif_data[tag] = str(value)
                
                metadata["exif"] = exif_data
                
                # Check for compression artifacts (simple heuristic)
                # High compression usually shows in file size relative to dimensions
                pixel_count = img.width * img.height
                bytes_per_pixel = metadata["size_bytes"] / pixel_count if pixel_count > 0 else 0
                metadata["bytes_per_pixel"] = round(bytes_per_pixel, 4)
                metadata["suspicious_compression"] = bytes_per_pixel < 0.1 and pixel_count > 1000000
                
                return metadata
        except Exception as e:
            return {"error": str(e)}
    
    def compute_perceptual_hash(self, image_path: str) -> Dict[str, str]:
        """Compute perceptual hash using ImageHash"""
        try:
            with Image.open(image_path) as img:
                return {
                    "phash": str(imagehash.phash(img)),
                    "dhash": str(imagehash.dhash(img)),
                    "ahash": str(imagehash.average_hash(img)),
                    "whash": str(imagehash.whash(img))
                }
        except Exception as e:
            return {"error": str(e)}
    
    def encode_image(self, image_path: str) -> str:
        """Encode image to base64 for API"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    
    async def analyze_with_openai(self, image_path: str, claim_reason: str) -> Dict[str, Any]:
        """Analyze image using OpenAI GPT-4 Vision API"""
        try:
            base64_image = self.encode_image(image_path)
            
            prompt = f"""Analyze this image of a product damage claim for a refund request.

Claim Reason: {claim_reason}

Carefully examine the image and determine:
1. Whether the damage appears genuine or artificially generated/manipulated
2. Signs of photo manipulation, AI generation, or Photoshop
3. Consistency of lighting and shadows
4. Whether the damage shown is consistent with the claim reason

Return a JSON object with exactly this structure:
{{
    "fraud_signal": <number between 0-100, higher means more suspicious>,
    "damage_detected": <boolean>,
    "ai_generated_probability": <number between 0-100>,
    "manipulation_detected": <boolean>,
    "reason": "<detailed explanation of your analysis>",
    "suspicious_indicators": ["<list of specific suspicious elements found>"]
}}

Be thorough and specific in your analysis."""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.2
            )
            
            # Parse JSON from response
            content = response.choices[0].message.content
            # Extract JSON if wrapped in code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            result = json.loads(content.strip())
            return result
            
        except Exception as e:
            return {
                "fraud_signal": 50,
                "damage_detected": False,
                "ai_generated_probability": 50,
                "manipulation_detected": True,
                "reason": f"Error during AI analysis: {str(e)}",
                "suspicious_indicators": ["analysis_failed"]
            }
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute evidence analysis
        
        Context must contain:
        - image_path: Path to the evidence image
        - claim_reason: Reason for the refund claim
        - claim_id: Unique claim identifier
        """
        image_path = context.get("image_path")
        claim_reason = context.get("claim_reason", "")
        claim_id = context.get("claim_id")
        
        if not image_path or not os.path.exists(image_path):
            return {
                "success": False,
                "error": "Image not found",
                "fraud_signal": 50
            }
        
        self.start_task(claim_id)
        self.log_event("image_analyzed", {"image_path": image_path})
        
        try:
            # Step 1: Extract metadata
            metadata = self.extract_metadata(image_path)
            
            # Step 2: Compute perceptual hash
            perceptual_hash = self.compute_perceptual_hash(image_path)
            
            # Step 3: AI analysis with OpenAI Vision
            ai_analysis = await self.analyze_with_openai(image_path, claim_reason)
            
            # Combine results
            result = {
                "success": True,
                "metadata": metadata,
                "perceptual_hash": perceptual_hash,
                "ai_analysis": ai_analysis,
                "fraud_signal": ai_analysis.get("fraud_signal", 50),
                "damage_detected": ai_analysis.get("damage_detected", False),
                "suspicious_indicators": ai_analysis.get("suspicious_indicators", []),
                "summary": ai_analysis.get("reason", "")
            }
            
            self.complete_task(result)
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "fraud_signal": 50
            }
            self.fail_task(str(e))
            return error_result
