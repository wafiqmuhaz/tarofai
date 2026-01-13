"""AI Agent HTTP client."""
import httpx
from app.config import settings


class AgentClient:
    """Client for communicating with AI Agent service."""
    
    def __init__(self):
        self.base_url = settings.agent_url
        self.timeout = 120.0  # 2 minutes for LLM processing
    
    async def search(self, query: str) -> dict:
        """
        Send search query to AI agent.
        
        Args:
            query: User's search query
            
        Returns:
            Dict with answer, sources, and cached status
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/process",
                json={"query": query}
            )
            response.raise_for_status()
            return response.json()
    
    async def health(self) -> bool:
        """Check if AI agent is healthy."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except Exception:
            return False
