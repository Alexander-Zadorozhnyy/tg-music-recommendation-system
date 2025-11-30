import os
from typing import Dict, Any, Optional
from audio_recognition.config import BACKEND_PORT
import httpx


class ContentExtractor:
    @staticmethod
    async def extract_content(user_data: Dict[str, Any], bot) -> str:
        content_type = user_data.get("content_type")
        
        if content_type == "text":
            return user_data.get("content", "")
        
        elif content_type in ["image"]:
            caption = user_data.get("caption", "")
            payload = {
                "file_path": f'{os.path.join(os.getcwd(), "downloads", user_data.get("content", ""))}',
            }
            async with httpx.AsyncClient() as client:
                response = await client.post(f"http://127.0.0.1:5555/recognize", json=payload)
                if response.status_code == 200:
                    return f'[ИЗОБРАЖЕНИЕ] {response.json()["text"]}. [Подпись к заданию] {caption}'
                return "[ИЗОБРАЖЕНИЕ - не удалось распознать]"
        
        elif content_type in ["audio", "voice"]:
            caption = user_data.get("caption", "")
            if content_type == "voice":
                payload = {
                    "file_path": f'{os.path.join(os.getcwd(), "downloads", user_data.get("content", ""))}.oga',
                    "with_punct": True
                }
                async with httpx.AsyncClient() as client:
                    response = await client.post(f"http://127.0.0.1:{BACKEND_PORT}/recognize", json=payload)
                    if response.status_code == 200:
                        return f'[АУДИО] {response.json()["text"]}. [Подпись к заданию] {caption}'
                    return "[АУДИО - не удалось распознать]"
        else:
            return "Ошибка"