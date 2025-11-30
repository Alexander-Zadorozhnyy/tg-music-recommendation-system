import aiohttp
import json
import os
from typing import Optional, Dict, Any

from app.config import settings

CATALOG_ID = settings.YANDEX_CATALOG_ID
API_TOKEN = settings.YANDEX_API_TOKEN


class YandexGPTService:
    @staticmethod
    async def call_yandex_gpt_async(user_prompt, system_prompt):
        url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {API_TOKEN}",
        }
        payload = {
            "modelUri": f"gpt://{CATALOG_ID}/yandexgpt/rc",
            "completionOptions": {"maxTokens": 8000, "temperature": 0.5},
            "messages": [
                {
                    "role": "system",
                    "text": system_prompt if system_prompt else "Ошибка",
                },
                {"role": "user", "text": user_prompt},
            ],
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return (
                        result.get("result", {})
                        .get("alternatives", [{}])[0]
                        .get("message", {})
                        .get("text", "")
                    )
                else:
                    error_text = await response.text()
                    return f"Ошибка API: {response.status} - {error_text}"

    @staticmethod
    async def call_with_json_response(user_prompt, system_prompt):
        response = await YandexGPTService.call_yandex_gpt_async(
            user_prompt, system_prompt
        )
        try:
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                return {"error": "Invalid JSON", "raw_response": response}
        except json.JSONDecodeError:
            return {"error": "Invalid JSON", "raw_response": response}
