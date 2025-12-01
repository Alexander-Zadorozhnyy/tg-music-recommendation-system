import json
from typing import List, Dict
from mistralai import Mistral
from .prompt_templates import RELEVANCE_PROMPT, MUSIC_RECOMMENDATION_PROMPT
from database.config import get_settings  
import asyncio
from functools import partial
import logging

# Инициализация клиента
_SETTINGS = get_settings()
_mistral_client = Mistral(api_key=_SETTINGS.MISTRAL_API_KEY)


async def call_llm(prompt: str, model: str = "mistral-small") -> str:
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            partial(
                _mistral_client.chat.complete,
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=200,
            )
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        print(f"Ошибка при вызове Mistral API: {e}")
        return ""


class LLMService:
    @staticmethod
    async def is_relevant(query: str) -> bool:
        """Проверяет, релевантен ли запрос теме музыки."""
        prompt = RELEVANCE_PROMPT.format(query=query)
        response = await call_llm(prompt, model="mistral-small")  
        return response.strip().upper() == "ДА"

    @staticmethod
    async def get_music_recommendations(query: str) -> List[Dict]:
        """Получает рекомендации по запросу от LLM."""
        prompt = MUSIC_RECOMMENDATION_PROMPT.format(query=query)
        response = await call_llm(prompt, model="mistral-medium")  
        try:
            data = json.loads(response)
            if not isinstance(data, dict) or "recommendations" not in data:
                return []
            recs = data["recommendations"]
            if not isinstance(recs, list):
                return []
            # Дополнительно: проверить структуру каждого элемента
            validated = []
            for item in recs:
                if isinstance(item, dict) and "artist" in item and "song" in item:
                    validated.append({"artist": str(item["artist"]), "song": str(item["song"])})
            return validated
        except json.JSONDecodeError:
            logging.warning(f"Invalid JSON from LLM: {response[:100]}...")
            return []