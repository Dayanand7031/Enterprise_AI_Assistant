from groq import Groq

from app.core.config import settings


client = Groq(
    api_key=settings.GROQ_API_KEY
)


def generate_response(message: str) -> str:
    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an enterprise AI assistant. "
                    "Answer clearly and concisely. "
                    "Use bullet points when appropriate. "
                    "Do not provide unnecessarily long explanations "
                    "unless the user asks for detail."
                ) 
            },
            {
                "role": "user",
                "content": message
            }
        ],
    )

    return response.choices[0].message.content