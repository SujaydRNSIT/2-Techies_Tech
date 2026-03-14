"""
Reverse image search using SerpAPI
"""
import os
import requests
from typing import Dict, Any, List, Optional

# Try to import serpapi, fallback to requests if not available
try:
    from serpapi import GoogleSearch
    SERPAPI_AVAILABLE = True
except ImportError:
    try:
        from google_search_results import GoogleSearch
        SERPAPI_AVAILABLE = True
    except ImportError:
        SERPAPI_AVAILABLE = False

class ImageSearchService:
    """
    Service for reverse image search using SerpAPI.
    Detects if images are reused online.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SERPAPI_API_KEY")
    
    def search_image(self, image_url: str) -> Dict[str, Any]:
        """
        Perform reverse image search
        """
        if not self.api_key or not SERPAPI_AVAILABLE:
            return self._simulate_search(image_url)
        
        try:
            params = {
                "api_key": self.api_key,
                "engine": "google_reverse_image",
                "image_url": image_url,
                "hl": "en",
                "gl": "us"
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            # Check for image results
            image_results = results.get("image_results", [])
            
            # Also check for knowledge graph
            knowledge_graph = results.get("knowledge_graph", {})
            
            return {
                "found_online": len(image_results) > 0,
                "matches_count": len(image_results),
                "source_urls": [r.get("link") for r in image_results[:5]],
                "titles": [r.get("title") for r in image_results[:5]],
                "knowledge_graph": knowledge_graph,
                "source": "serpapi_live"
            }
            
        except Exception as e:
            print(f"SerpAPI error: {e}")
            return self._simulate_search(image_url)
    
    def search_local_image(self, image_path: str) -> Dict[str, Any]:
        """
        Search for a local image by uploading it first
        Note: This requires uploading the image to a temporary URL first
        For demo, we'll use simulation if no direct URL available
        """
        # In production, you'd upload to S3 or similar first
        # For now, simulate
        return self._simulate_search(image_path)
    
    def _simulate_search(self, image_path: str) -> Dict[str, Any]:
        """
        Simulated image search for demo purposes
        Uses image hash to provide consistent "random" results
        """
        import hashlib
        
        # Generate deterministic result based on image path
        hash_val = int(hashlib.md5(image_path.encode()).hexdigest(), 16)
        
        # 20% chance of finding image online (for demo variety)
        found_online = (hash_val % 100) < 20
        
        if found_online:
            matches = (hash_val % 5) + 1
            return {
                "found_online": True,
                "matches_count": matches,
                "source_urls": [
                    "https://example.com/image1.jpg",
                    "https://socialmedia.com/post/123",
                ][:matches],
                "titles": [
                    "Stock Photo - Damaged Product",
                    "Social Media Post",
                ][:matches],
                "knowledge_graph": {},
                "source": "serpapi_simulated",
                "note": "Simulated result - SerpAPI key not configured"
            }
        else:
            return {
                "found_online": False,
                "matches_count": 0,
                "source_urls": [],
                "titles": [],
                "knowledge_graph": {},
                "source": "serpapi_simulated",
                "note": "Simulated result - SerpAPI key not configured"
            }

# Global service instance
image_search_service = ImageSearchService()
