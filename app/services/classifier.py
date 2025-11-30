from typing import Dict, Any
from app.services.llm_service import YandexGPTService
from app.services.prompts import EducationalPrompts


class QuestionClassifier:
    @staticmethod
    async def classify_question(question: str) -> Dict[str, Any]:
        system_prompt = EducationalPrompts.get_classification_prompt()
        user_prompt = f"Классифицируй этот вопрос: {question}"

        result = await YandexGPTService.call_with_json_response(
            user_prompt, system_prompt
        )

        if "error" in result:
            return {
                "is_academic": False,
                "subject": "other",
                "difficulty": "простая",
                "solution_type": "мгновенный",
                "task_type": "other",
                "error": result.get("error", "Classification failed"),
            }

        required_fields = [
            "is_academic",
            "subject",
            "difficulty",
            "solution_type",
            "task_type",
        ]
        for field in required_fields:
            if field not in result:
                result[field] = "other" if field != "is_academic" else False

        return result
