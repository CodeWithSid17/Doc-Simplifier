"""
Saral AI service.

Groq is used as the current LLM provider. The mobile application never sees
the provider API key; all AI requests stay behind Django.
"""
import json
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"


class SimplifierError(Exception):
    pass


def _call_groq(system_prompt, user_prompt, timeout=60):
    if not settings.GROQ_API_KEY:
        raise SimplifierError("AI service is not configured on the server.")

    payload = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.25,
        "response_format": {"type": "json_object"},
    }

    try:
        response = requests.post(
            GROQ_ENDPOINT,
            json=payload,
            headers={
                "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            timeout=timeout,
        )
        response.raise_for_status()
    except requests.exceptions.Timeout as exc:
        raise SimplifierError("The AI service took too long to respond.") from exc
    except requests.exceptions.RequestException as exc:
        logger.exception("Groq request failed")
        raise SimplifierError("Could not reach the AI service right now.") from exc

    try:
        content = response.json()["choices"][0]["message"]["content"]
        return json.loads(content)
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
        logger.exception("Invalid Groq response")
        raise SimplifierError("The AI returned an unexpected response.") from exc


def simplify_document(text: str, audience: str = "adult", language: str = "en") -> dict:
    from .prompts import SYSTEM_PROMPT, build_user_prompt

    result = _call_groq(
        SYSTEM_PROMPT,
        build_user_prompt(text, audience, language),
        timeout=60,
    )
    simplified = str(result.get("simplified", "")).strip()
    summary = str(result.get("summary_line", "")).strip()

    if not summary and simplified:
        summary = simplified.split(".")[0].strip() + "."

    return {
        "simplified": simplified,
        "warnings": result.get("warnings", []) or [],
        "actions": result.get("actions", []) or [],
        "summary_line": summary,
    }


def analyze_document(text: str, language: str = "en") -> dict:
    prompt = f"""
Analyze the following document for an ordinary user.

Return ONLY JSON with this exact structure:
{{
  "summary": "short plain-language summary",
  "key_points": ["..."],
  "warnings": ["..."],
  "actions": ["..."],
  "important_dates": ["..."],
  "glossary": [{{"term": "...", "meaning": "..."}}]
}}

Rules:
- Use only information present in the document.
- Do not invent dates, fees, obligations or facts.
- Keep each item concise.
- If a section has nothing useful, return an empty list.
- Write the result in {language}.

DOCUMENT:
---
{text[:30000]}
---
"""
    return _call_groq(
        "You are Saral, a careful document analysis assistant. Never invent facts.",
        prompt,
        timeout=90,
    )


def answer_document_question(text: str, question: str) -> dict:
    prompt = f"""
Answer the user's question using ONLY the document below.

Return ONLY JSON:
{{
  "answer": "clear plain-language answer",
  "evidence": ["short supporting points from the document"]
}}

If the document does not contain enough information, say so clearly.
Do not invent information. This is not legal, medical or financial advice.

DOCUMENT:
---
{text[:30000]}
---

QUESTION:
{question}
"""
    return _call_groq(
        "You are Saral's document-aware AI assistant.",
        prompt,
        timeout=90,
    )


def translate_text(text: str, language: str) -> dict:
    prompt = f"""
Translate and simplify the following text naturally into {language}.

Return ONLY JSON:
{{
  "translated": "translated text"
}}

Do not add facts.
TEXT:
---
{text[:20000]}
---
"""
    return _call_groq(
        "You are a precise translation assistant.",
        prompt,
        timeout=90,
    )


def compare_documents(text_a: str, text_b: str) -> dict:
    prompt = f"""
Compare the two documents.

Return ONLY JSON:
{{
  "summary": "plain-language comparison",
  "differences": ["important difference"],
  "similarities": ["important similarity"],
  "attention": ["difference that deserves attention"]
}}

Do not invent information.

DOCUMENT A:
---
{text_a[:20000]}
---

DOCUMENT B:
---
{text_b[:20000]}
---
"""
    return _call_groq(
        "You are Saral's document comparison assistant.",
        prompt,
        timeout=120,
    )
