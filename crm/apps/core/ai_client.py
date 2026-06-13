from openai import OpenAI
from django.conf import settings

DEFAULT_MODEL = "deepseek/deepseek-v3.2"


def get_ai_client() -> OpenAI:
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=settings.OPENROUTER_API_KEY,
        default_headers={
            "HTTP-Referer": settings.SITE_URL,
            "X-Title": "Xeno CRM",
        },
    )


def get_model() -> str:
    return getattr(settings, 'OPENROUTER_MODEL', DEFAULT_MODEL)
