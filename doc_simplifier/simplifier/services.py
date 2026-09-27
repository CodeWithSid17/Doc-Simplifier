"""
LLM integration for the Document Simplifier.

Uses Groq's free-tier API (OpenAI-compatible chat completions endpoint).
Swap GROQ_API_KEY / GROQ_MODEL in settings.py or .env if you switch providers
(e.g. Gemini) later — only this file needs to change.
"""
import json
import logging

import requests
from django.conf import settings

from .prompts import SYSTEM_PROMPT, build_user_prompt

logger = logging.getLogger(__name__)

GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"


class SimplifierError(Exception):
    """Raised when the LLM call or response parsing fails."""
    pass


def simplify_document(text: str, audience: str = "adult", language: str = "en") -> dict:
    """
    Calls the LLM and returns a dict:
        {"simplified": str, "warnings": [str], "actions": [str], "summary_line": str}
    Raises SimplifierError on any failure so the view can return a clean 502/400.
    """
    if not settings.GROQ_API_KEY:
        raise SimplifierError(
            "Server is missing GROQ_API_KEY. Add it to your .env file."
        )

    if not text or not text.strip():
        raise SimplifierError("No text provided to simplify.")

    payload = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(text, audience, language)},
        ],
        "temperature": 0.3,
        "response_format": {"type": "json_object"},
    }

    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(GROQ_ENDPOINT, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        raise SimplifierError("The AI service took too long to respond. Please try again.")
    except requests.exceptions.RequestException as exc:
        logger.error("Groq API request failed: %s", exc)
        raise SimplifierError("Could not reach the AI service right now.")

    try:
        raw_content = response.json()["choices"][0]["message"]["content"]
        parsed = json.loads(raw_content)
    except (KeyError, IndexError, json.JSONDecodeError) as exc:
        logger.error("Failed to parse Groq response: %s", exc)
        raise SimplifierError("The AI returned an unexpected response. Please try again.")

    simplified_text = parsed.get("simplified", "").strip()
    summary_line = parsed.get("summary_line", "").strip()

    # Safety net: never trust the model to follow instructions 100% of the time.
    # If it forgot summary_line, derive a reasonable one from the simplified text
    # instead of shipping a blank field to the app.
    if not summary_line and simplified_text:
        first_sentence = simplified_text.split(". ")[0].strip()
        summary_line = first_sentence if first_sentence.endswith((".", "!", "?")) else first_sentence + "."

    return {
        "simplified": simplified_text,
        "warnings": parsed.get("warnings", []) or [],
        "actions": parsed.get("actions", []) or [],
        "summary_line": summary_line,
    }