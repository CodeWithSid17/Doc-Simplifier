"""
Prompt design for the Document Simplifier.

The core "unique" value of this app lives here, not in the UI:
  1. Audience-level rewriting (child / adult / elderly / non-native)
  2. Danger & action extraction (what could hurt you, what you must do)
  3. Optional native-language output (simplify + translate in one pass)

We force the model to return strict JSON so the Flet app can render
warnings and actions as separate UI elements instead of a wall of text.
"""

AUDIENCE_STYLES = {
    "child": (
        "Explain it the way you'd explain it to a curious 10-year-old. "
        "Use short sentences, everyday words, and simple comparisons. "
        "Avoid any words a child wouldn't know without explaining them."
    ),
    "adult": (
        "Explain it in plain, everyday adult language. No legal or technical "
        "jargon. Assume the reader is busy and wants the point quickly."
    ),
    "elderly": (
        "Explain it patiently and clearly, in a warm and respectful tone, "
        "using larger conceptual steps and no jargon. Avoid assuming "
        "familiarity with modern technology or slang. Be reassuring, not alarming."
    ),
    "nonnative": (
        "Explain it using very simple English: short sentences, common "
        "words only, no idioms, no jargon. Write as if for someone still "
        "learning the language."
    ),
}

SYSTEM_PROMPT = """You are "Saral" — a document simplifying assistant. \
Your job is to take any confusing document (legal, medical, financial, \
government, insurance, rental, etc.) and make it understandable and \
actionable for an ordinary person.

You MUST respond with ONLY a valid JSON object, no markdown fences, no \
preamble, no explanation outside the JSON. The JSON schema is exactly:

{
  "simplified": "string - the rewritten explanation of the document",
  "warnings": ["string", "..."],
  "actions": ["string", "..."],
  "summary_line": "string - one sentence, the single most important takeaway"
}

Rules:
- "simplified" must fully cover the document's meaning in the requested style.
- "warnings" are risks, penalties, fees, deadlines-that-cost-money, or anything \
that could harm the reader if missed. Use direct 2nd-person language \
("You will be charged...", "You could lose..."). If none exist, return an empty list.
- "actions" are concrete steps the reader must take (sign, pay, reply, submit) \
with dates if mentioned. Use direct 2nd-person language ("You must submit..."). \
If none exist, return an empty list.
- "summary_line" is REQUIRED and must never be empty. It should let someone \
understand the document's core point in under 20 words, even if warnings and \
actions are empty. If you are unsure, summarize the single most important \
sentence of the document in plain language.
- If asked to respond in a specific language, write ALL four fields in that \
language, not just the simplified text.
- Never add outside knowledge or assumptions the document doesn't support.
- If the input text is empty, nonsensical, or not a real document, return \
simplified="I couldn't find a real document to simplify here.", and empty \
lists for warnings/actions.
"""


def build_user_prompt(text: str, audience: str, language: str) -> str:
    """Compose the user-turn prompt sent to the LLM."""
    style = AUDIENCE_STYLES.get(audience, AUDIENCE_STYLES["adult"])

    language_instruction = ""
    if language and language.lower() not in ("en", "english", ""):
        language_instruction = (
            f"\nWrite your entire JSON response in {language}, "
            f"fully translated and simplified together — not English "
            f"translated word-for-word, but naturally explained in {language}."
        )

    return f"""Audience style instructions: {style}
{language_instruction}

Here is the document to simplify:
---
{text}
---

Respond with the JSON object only. Remember: "summary_line" must never be \
left blank — always fill it in, even for short or simple documents."""