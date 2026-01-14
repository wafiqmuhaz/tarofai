"""OpenRouter API client for LLM inference with retry logic."""
import os
import asyncio
import httpx
from dotenv import load_dotenv

load_dotenv()


class RateLimitError(Exception):
    """Raised when API rate limit is exceeded after all retries."""
    pass


class OpenRouterClient:
    """Client for OpenRouter API with retry support."""
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        self.model = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-exp:free")
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not set in environment")
        
        # Retry configuration
        self.max_retries = 3
        self.base_delay = 2  # seconds
    
    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generate response from LLM with retry logic for rate limits.
        
        Args:
            system_prompt: System instruction
            user_prompt: User's message
            
        Returns:
            Generated text response
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=120.0) as client:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json",
                            "HTTP-Referer": "https://tarofa.local",
                            "X-Title": "Tarofa Islamic Search"
                        },
                        json={
                            "model": self.model,
                            "messages": [
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_prompt}
                            ],
                            "temperature": 0.7,
                            "max_tokens": 2048
                        }
                    )
                    
                    if response.status_code == 429:
                        # Rate limited - wait and retry
                        delay = self.base_delay * (2 ** attempt)
                        print(f"[LLM] Rate limited. Waiting {delay}s before retry {attempt + 1}/{self.max_retries}...")
                        await asyncio.sleep(delay)
                        continue
                    
                    response.raise_for_status()
                    data = response.json()
                    
                    return data["choices"][0]["message"]["content"]
                    
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    delay = self.base_delay * (2 ** attempt)
                    print(f"[LLM] Rate limited. Waiting {delay}s before retry {attempt + 1}/{self.max_retries}...")
                    await asyncio.sleep(delay)
                    last_error = e
                    continue
                raise
            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    delay = self.base_delay * (2 ** attempt)
                    print(f"[LLM] Error: {e}. Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                    continue
                raise
        
        # All retries exhausted
        raise RateLimitError(f"API rate limit exceeded after {self.max_retries} retries. Please wait a moment and try again.")
    
    async def health_check(self) -> bool:
        """Check if OpenRouter API is accessible."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                return response.status_code == 200
        except Exception:
            return False
