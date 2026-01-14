"""OpenRouter API client with ROBUST rate limit handling and model fallback."""
import os
import asyncio
import random
import httpx
from dotenv import load_dotenv

load_dotenv()


class RateLimitError(Exception):
    """Raised when API rate limit is exceeded after all retries."""
    pass


class OpenRouterClient:
    """Client for OpenRouter API with model fallback and robust retry."""
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not set in environment")
        
        # Primary model from env, with fallbacks
        primary_model = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-exp:free")
        
        # Model fallback chain - VALID OpenRouter free models
        self.models = [
            primary_model,
            "google/gemma-2-9b-it:free",
            "meta-llama/llama-3.1-8b-instruct:free",
            "mistralai/mistral-7b-instruct:free",
            "meta-llama/llama-3.1-405b-instruct:free",
            "xiaomi/mimo-v2-flash:free",
            "deepseek/deepseek-r1-0528:free",
            "meta-llama/llama-3.3-70b-instruct:free",
            "google/gemma-3-27b-it:free",
            "openai/gpt-oss-120b:free",
            "openai/gpt-oss-20b:free",
            "mistralai/mistral-small-3.1-24b-instruct:free",
            "meta-llama/llama-3.2-3b-instruct:free",
            "qwen/qwen3-4b:free",
            "google/gemma-3-4b-it:free",
            "google/gemma-3-12b-it:free"
        ]
        # Remove duplicates while preserving order
        self.models = list(dict.fromkeys(self.models))
        
        # Current model index
        self._current_model_index = 0
        
        # Retry configuration - more aggressive
        self.timeout = 60.0  # Reasonable timeout
        self.max_retries_per_model = 2
        self.base_delay = 3  # Increased from 1s
        self.max_delay = 30  # Max delay cap
        
        # Content limits
        self.max_content_per_source = 2000
        self.max_sources = 3
        
        # Token settings by intent
        self.token_settings = {
            "simple": {"max_tokens": 800, "temperature": 0.5},
            "moderate": {"max_tokens": 1024, "temperature": 0.6},
            "complex": {"max_tokens": 1500, "temperature": 0.7},
        }
    
    def _get_current_model(self) -> str:
        """Get current model in fallback chain."""
        return self.models[self._current_model_index]
    
    def _next_model(self) -> bool:
        """Move to next model in fallback chain. Returns False if no more models."""
        if self._current_model_index < len(self.models) - 1:
            self._current_model_index += 1
            print(f"[LLM] Switching to fallback model: {self._get_current_model()}")
            return True
        return False
    
    def _reset_model(self):
        """Reset to primary model."""
        self._current_model_index = 0
    
    def _get_token_settings(self, intent: str = "general") -> dict:
        """Get token settings based on query intent."""
        simple_intents = {"definisi", "hukum"}
        complex_intents = {"dalil", "konsekuensi", "cara", "syarat"}
        
        if intent in simple_intents:
            return self.token_settings["simple"]
        elif intent in complex_intents:
            return self.token_settings["complex"]
        else:
            return self.token_settings["moderate"]
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay with exponential backoff and jitter."""
        # Exponential backoff: base_delay * 2^attempt
        delay = self.base_delay * (2 ** attempt)
        # Add random jitter (±20%)
        jitter = delay * 0.2 * (random.random() * 2 - 1)
        # Cap at max delay
        return min(delay + jitter, self.max_delay)
    
    async def generate(self, system_prompt: str, user_prompt: str, intent: str = "general") -> str:
        """
        Generate response from LLM with robust rate limit handling.
        
        Features:
        - Exponential backoff with jitter
        - Automatic model fallback on rate limit
        - Multiple retry attempts per model
        
        Args:
            system_prompt: System instruction
            user_prompt: User's message
            intent: Query intent for adaptive token limits
            
        Returns:
            Generated text response
        """
        token_settings = self._get_token_settings(intent)
        
        # Reset to primary model at start of new request
        self._reset_model()
        
        total_attempts = 0
        max_total_attempts = len(self.models) * self.max_retries_per_model
        
        while total_attempts < max_total_attempts:
            current_model = self._get_current_model()
            model_attempt = total_attempts % self.max_retries_per_model
            
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    print(f"[LLM] Using model: {current_model} (attempt {model_attempt + 1})")
                    
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json",
                            "HTTP-Referer": "https://tarofa.local",
                            "X-Title": "Tarofa Islamic Search"
                        },
                        json={
                            "model": current_model,
                            "messages": [
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_prompt}
                            ],
                            "temperature": token_settings["temperature"],
                            "max_tokens": token_settings["max_tokens"]
                        }
                    )
                    
                    if response.status_code == 429:
                        # Rate limited
                        total_attempts += 1
                        
                        # Check if should switch model
                        if (model_attempt + 1) >= self.max_retries_per_model:
                            if not self._next_model():
                                # No more models, raise error
                                raise RateLimitError(
                                    f"All models rate limited after {total_attempts} attempts. "
                                    "Please wait 1-2 minutes and try again."
                                )
                        
                        # Calculate delay
                        delay = self._calculate_delay(model_attempt)
                        print(f"[LLM] Rate limited. Waiting {delay:.1f}s before retry...")
                        await asyncio.sleep(delay)
                        continue
                    
                    if response.status_code == 404:
                        # Model not found - skip to next model immediately
                        print(f"[LLM] Model '{current_model}' not found (404), trying next...")
                        total_attempts += 1
                        if not self._next_model():
                            raise ValueError(f"All models failed. Last error: 404 for {current_model}")
                        continue
                    
                    response.raise_for_status()
                    data = response.json()
                    
                    # Success! Log which model worked
                    if self._current_model_index > 0:
                        print(f"[LLM] ✓ Success with fallback model: {current_model}")
                    else:
                        print(f"[LLM] ✓ Success with primary model")
                    
                    return data["choices"][0]["message"]["content"]
                    
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    total_attempts += 1
                    
                    if (model_attempt + 1) >= self.max_retries_per_model:
                        if not self._next_model():
                            raise RateLimitError(
                                f"All models rate limited. Please wait 1-2 minutes."
                            )
                    
                    delay = self._calculate_delay(model_attempt)
                    print(f"[LLM] Rate limited (HTTP error). Waiting {delay:.1f}s...")
                    await asyncio.sleep(delay)
                    continue
                raise
                
            except asyncio.TimeoutError:
                total_attempts += 1
                print(f"[LLM] Timeout on attempt {total_attempts}")
                
                # On timeout, try next model immediately
                if not self._next_model():
                    raise TimeoutError("All models timed out")
                continue
                
            except Exception as e:
                total_attempts += 1
                print(f"[LLM] Error: {str(e)[:50]}")
                
                if total_attempts < max_total_attempts:
                    delay = self._calculate_delay(model_attempt)
                    print(f"[LLM] Retrying in {delay:.1f}s...")
                    await asyncio.sleep(delay)
                    continue
                raise
        
        # Should not reach here, but just in case
        raise RateLimitError(
            f"Failed after {total_attempts} attempts across {len(self.models)} models. "
            "Please wait a few minutes and try again."
        )
    
    async def generate_stream(self, system_prompt: str, user_prompt: str, intent: str = "general"):
        """
        Generate streaming response from LLM.
        
        Yields tokens as they arrive from OpenRouter streaming API.
        
        Args:
            system_prompt: System instruction
            user_prompt: User's message
            intent: Query intent for adaptive token limits
            
        Yields:
            dict with type and content: {"type": "token", "content": "..."} or {"type": "done"}
        """
        token_settings = self._get_token_settings(intent)
        
        # Reset to primary model at start of new request
        self._reset_model()
        
        total_attempts = 0
        max_total_attempts = len(self.models) * self.max_retries_per_model
        
        while total_attempts < max_total_attempts:
            current_model = self._get_current_model()
            model_attempt = total_attempts % self.max_retries_per_model
            
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    print(f"[LLM STREAM] Using model: {current_model} (attempt {model_attempt + 1})")
                    
                    async with client.stream(
                        "POST",
                        f"{self.base_url}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json",
                            "HTTP-Referer": "https://tarofa.local",
                            "X-Title": "Tarofa Islamic Search"
                        },
                        json={
                            "model": current_model,
                            "messages": [
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_prompt}
                            ],
                            "temperature": token_settings["temperature"],
                            "max_tokens": token_settings["max_tokens"],
                            "stream": True
                        }
                    ) as response:
                        if response.status_code == 429:
                            # Rate limited - retry with backoff
                            total_attempts += 1
                            if (model_attempt + 1) >= self.max_retries_per_model:
                                if not self._next_model():
                                    raise RateLimitError("All models rate limited.")
                            delay = self._calculate_delay(model_attempt)
                            print(f"[LLM STREAM] Rate limited. Waiting {delay:.1f}s...")
                            await asyncio.sleep(delay)
                            continue
                        
                        if response.status_code == 404:
                            print(f"[LLM STREAM] Model '{current_model}' not found, trying next...")
                            total_attempts += 1
                            if not self._next_model():
                                raise ValueError(f"All models failed.")
                            continue
                        
                        response.raise_for_status()
                        
                        # Successfully connected - stream tokens
                        if self._current_model_index > 0:
                            print(f"[LLM STREAM] ✓ Streaming with fallback model: {current_model}")
                        else:
                            print(f"[LLM STREAM] ✓ Streaming with primary model")
                        
                        # Parse SSE stream
                        async for line in response.aiter_lines():
                            if not line:
                                continue
                            
                            if line.startswith("data: "):
                                data = line[6:]  # Remove "data: " prefix
                                
                                if data == "[DONE]":
                                    yield {"type": "done"}
                                    return
                                
                                try:
                                    import json
                                    chunk = json.loads(data)
                                    choices = chunk.get("choices", [])
                                    if choices:
                                        delta = choices[0].get("delta", {})
                                        content = delta.get("content", "")
                                        if content:
                                            yield {"type": "token", "content": content}
                                except json.JSONDecodeError:
                                    continue
                        
                        # Stream completed successfully
                        yield {"type": "done"}
                        return
                        
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    total_attempts += 1
                    if (model_attempt + 1) >= self.max_retries_per_model:
                        if not self._next_model():
                            raise RateLimitError("All models rate limited.")
                    delay = self._calculate_delay(model_attempt)
                    await asyncio.sleep(delay)
                    continue
                raise
                
            except asyncio.TimeoutError:
                total_attempts += 1
                print(f"[LLM STREAM] Timeout on attempt {total_attempts}")
                if not self._next_model():
                    raise TimeoutError("All models timed out")
                continue
                
            except Exception as e:
                total_attempts += 1
                print(f"[LLM STREAM] Error: {str(e)[:50]}")
                if total_attempts < max_total_attempts:
                    delay = self._calculate_delay(model_attempt)
                    await asyncio.sleep(delay)
                    continue
                raise
        
        raise RateLimitError(f"Streaming failed after {total_attempts} attempts.")
    
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
    
    def get_available_models(self) -> list[str]:
        """Get list of fallback models."""
        return self.models.copy()
