from mistralai import Mistral
from .prompt_templates import RELEVANCE_PROMPT
from database.config import get_settings
import asyncio
from functools import partial
import logging

# Инициализация клиента
_SETTINGS = get_settings()
_mistral_client = Mistral(api_key=_SETTINGS.MISTRAL_API_KEY)


async def call_llm(prompt: str, model: str = "mistral-small") -> str:
    """Вызов LLM с обработкой ошибок."""
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
            ),
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        logging.error(f"Ошибка при вызове Mistral API: {e}")
        return ""


class LLMService:
    @staticmethod
    async def is_relevant(query: str) -> bool:
        """Проверяет, релевантен ли запрос теме музыки."""
        prompt = RELEVANCE_PROMPT.format(query=query)
        response = await call_llm(prompt, model="mistral-small")
        # Ожидаем ответ "ДА" или "НЕТ"
        return response.strip().upper() == "ДА"
