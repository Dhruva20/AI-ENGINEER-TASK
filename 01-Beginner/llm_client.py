import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2


class LLMError(Exception):
    """Raised with a friendly message when the AI call fails."""


def _is_temporary(msg: str) -> bool:
    return any(k in msg for k in ("503", "unavailable", "overloaded", "high demand", "429", "timeout"))


def generate(prompt: str) -> str:
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise LLMError("API key not found. Add API_KEY=... to your .env file.")

    model = os.getenv("MODEL_NAME", "gemini-3.8-flash")
    client = genai.Client(api_key=api_key)

    response = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(model=model, contents=prompt)
            break
        except Exception as e:
            msg = str(e).lower()

            if _is_temporary(msg) and attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY_SECONDS * attempt)  # wait 2s, then 4s
                continue

            if any(k in msg for k in ("api key", "401", "403", "permission")):
                raise LLMError("Your API key looks invalid. Check the .env file.")
            if "404" in msg or "not_found" in msg:
                raise LLMError(f"Model '{model}' was not found. Check MODEL_NAME in .env.")
            if any(k in msg for k in ("503", "unavailable", "high demand", "overloaded")):
                raise LLMError("The AI service is busy right now. Please try again in a minute.")
            if any(k in msg for k in ("429", "quota", "rate", "exhausted")):
                raise LLMError("Rate limit reached. Wait a minute and try again.")
            if any(k in msg for k in ("timeout", "connection", "network")):
                raise LLMError("Network problem. Check your internet and try again.")
            raise LLMError(f"The AI service failed: {e}")

    text = getattr(response, "text", None)
    if not text or not text.strip():
        raise LLMError("The model returned an empty response. Try rephrasing your input.")
    return text.strip()