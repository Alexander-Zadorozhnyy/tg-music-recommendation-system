import os
import logging
import httpx

logger = logging.getLogger(__name__)


async def call_mistral(prompt: str, model: str = "mistral-small-latest") -> str:
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY is not set in environment variables")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.6,
                    "max_tokens": 400,
                },
                timeout=10,
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"].strip()
            return content

    except Exception as e:
        logger.error(f"Ошибка вызова Mistral API: {e}")
        raise
