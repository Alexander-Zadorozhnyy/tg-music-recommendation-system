from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from services.prompts import EducationalPrompts


@dataclass
class ConversationMessage:
    role: str
    content: str
    timestamp: Optional[str] = None


@dataclass
class StepByStepSession:
    original_question: str
    subject: str
    difficulty: str
    messages: List[ConversationMessage] = field(default_factory=list)
    step_count: int = 0
    is_completed: bool = False

    def add_message(self, role, content):
        self.messages.append(ConversationMessage(role=role, content=content))
        if role == "assistant":
            self.step_count += 1

    def get_formatted_history(self):
        if not self.messages:
            return "Диалог только начинается."

        history = ""
        for msg in self.messages:
            if msg.role == "assistant":
                history += f"Наставник: {msg.content}\n\n"
            elif msg.role == "user":
                history += f"Школьник: {msg.content}\n\n"

        return history.strip()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_question": self.original_question,
            "subject": self.subject,
            "difficulty": self.difficulty,
            "messages": [
                {"role": msg.role, "content": msg.content} for msg in self.messages
            ],
            "step_count": self.step_count,
            "is_completed": self.is_completed,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StepByStepSession":
        session = cls(
            original_question=data["original_question"],
            subject=data["subject"],
            difficulty=data["difficulty"],
            step_count=data.get("step_count", 0),
            is_completed=data.get("is_completed", False),
        )

        for msg_data in data.get("messages", []):
            session.messages.append(
                ConversationMessage(role=msg_data["role"], content=msg_data["content"])
            )

        return session


class ConversationManager:
    @staticmethod
    async def start_session(
        question: str, classification: Dict[str, Any]
    ) -> StepByStepSession:
        session = StepByStepSession(
            original_question=question,
            subject=classification.get("subject", "математика"),
            difficulty=classification.get("difficulty", "средняя"),
        )

        return session

    @staticmethod
    async def continue_conversation(
        session: StepByStepSession, user_response: str, llm_service
    ) -> str:
        session.add_message("user", user_response)

        user_prompt = f"""ИСХОДНЫЙ ЗАПРОС: {session.original_question}
ПРЕДМЕТ: {session.subject}
СЛОЖНОСТЬ: {session.difficulty}

ИСТОРИЯ ДИАЛОГА:
{session.get_formatted_history()}

ЗАДАЧА:Ты уже ведешь диалог со школьником по этой задаче. Анализируй имеющуюся историю диалога, учитывай инструкцию выше и продолжай диалог пока это необходимо. Учитывай, что исходное условие задачи может быть в виде LATEX кода.

Если школьник решил задачу правильно - похвали его и подведи итоги.
Если школьник застрял - дай более конкретную подсказку.
Если ответ неверный -  исправь и объясни
Если студент просит готовый ответ - дай его с подробным объяснением."""

        system_prompt = EducationalPrompts.get_step_by_step_prompt()

        assistant_response = await llm_service.call_yandex_gpt_async(
            user_prompt=user_prompt, system_prompt=system_prompt
        )

        session.add_message("assistant", assistant_response)

        return assistant_response
