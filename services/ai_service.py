import os


# Если планируете использовать OpenAI: import openai

class AIService:
    @staticmethod
    def get_ai_response(message: str) -> str:
        """
        Заглушка для AI сервиса.
        Здесь должен быть код запроса к OpenAI/Anthropic.
        """
        # Пример реализации:
        # return openai.ChatCompletion.create(...).choices[0].message.content

        return f"Эмуляция ответа AI на ваш запрос: {message}\n(Подключите API ключи в services/ai_service.py)"