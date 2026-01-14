"""AI Agent HTTP client."""
import httpx
from app.config import settings
from typing import AsyncGenerator


class AgentClient:
    """Client for communicating with AI Agent service."""
    
    def __init__(self):
        self.base_url = settings.agent_url
        self.timeout = 60.0  # Reduced from 120s - optimized agent is faster
    
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
    
    async def search_stream(self, query: str) -> AsyncGenerator[str, None]:
        """
        Send search query to AI agent with streaming response.
        
        Yields SSE events from the agent.
        
        Args:
            query: User's search query
            
        Yields:
            Raw SSE event strings from AI Agent
        """
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/process-stream",
                json={"query": query}
            ) as response:
                response.raise_for_status()
                
                # Forward SSE events as they arrive
                async for line in response.aiter_lines():
                    if line:
                        yield line + "\n"
                        # Add extra newline for SSE event separation
                        if line.startswith("data:"):
                            yield "\n"
    
    async def health(self) -> bool:
        """Check if AI agent is healthy."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except Exception:
            return False
