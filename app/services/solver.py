from typing import Dict, Any
from app.services.llm_service import YandexGPTService
from app.services.prompts import EducationalPrompts


class MathSolver:
    @staticmethod
    async def solve_instant(question: str, classification: Dict[str, Any]) -> str:
        system_prompt = EducationalPrompts.get_instant_solution_prompt()
        user_prompt = f"Реши задачу: {question}"

        return await YandexGPTService.call_yandex_gpt_async(user_prompt, system_prompt)

    @staticmethod
    async def solve_step_by_step(question: str, classification: Dict[str, Any]) -> str:
        system_prompt = EducationalPrompts.get_step_by_step_prompt()
        user_prompt = f"Помоги студенту разобрать эту задачу пошагово: {question}"

        return await YandexGPTService.call_yandex_gpt_async(user_prompt, system_prompt)

    @staticmethod
    def get_non_academic_response() -> str:
        return EducationalPrompts.get_non_academic_response()
