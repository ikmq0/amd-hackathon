"""Layer 3 — Explain: turn clean, already-categorized spend aggregates into a short
Arabic monthly report or a chat answer.

Ported from the Khawarizm engine's ``engine/explain.py``. The design guarantee is
unchanged: the LLM only ever phrases text over aggregates that the deterministic
pipeline already produced — it never sees a raw descriptor and never categorizes
anything, so there is nothing for it to hallucinate. Token cost stays tiny.
"""

from __future__ import annotations

import time

from app.core.config import settings

_client = None
_MAX_RETRIES = 3


class LLMUnavailable(RuntimeError):
    """Raised when a Gemini call is requested but no API key is configured."""


def _get_client():
    """Lazily build the Gemini client; fail loudly if the key is missing."""
    global _client
    if not settings.gemini_api_key:
        raise LLMUnavailable(
            "GEMINI_API_KEY is not set — add it to backend/.env to enable the report and chat."
        )
    if _client is None:
        from google import genai  # imported lazily so the app boots without the package

        _client = genai.Client(api_key=settings.gemini_api_key)
    return _client


def llm_enabled() -> bool:
    return bool(settings.gemini_api_key)


# ---------------------------------------------------------------------------
# Aggregate formatting — the exact text the model is grounded on
# ---------------------------------------------------------------------------
def _format_aggregate_lines(aggregate: list[dict]) -> str:
    return "\n".join(
        f"- {row['category']}: {row['count']} عملية، إجمالي {abs(row['total']):.2f} ريال"
        for row in aggregate
    )


def _generate(prompt: str) -> str:
    client = _get_client()
    last_exc: Exception | None = None
    for attempt in range(_MAX_RETRIES):
        try:
            resp = client.models.generate_content(model=settings.gemini_model, contents=prompt)
            text = (resp.text or "").strip()
            if text:
                return text
            last_exc = RuntimeError("empty LLM response")
        except Exception as exc:  # noqa: BLE001 - transient (429/5xx/network); retry with backoff
            last_exc = exc
        if attempt < _MAX_RETRIES - 1:
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"LLM call failed after {_MAX_RETRIES} attempts: {last_exc}")


# ---------------------------------------------------------------------------
# report / chat
# ---------------------------------------------------------------------------
def generate_report(aggregate: list[dict], month_label: str) -> str:
    """Return a short Arabic markdown monthly report over the given spend aggregate."""
    total_spend = sum(abs(row["total"]) for row in aggregate)
    prompt = (
        "أنت مساعد مالي شخصي. اكتب تقريراً شهرياً موجزاً بالعربية (فقرة أو فقرتين ثم نقاط) "
        "بالاعتماد فقط على البيانات المجمّعة التالية. لا تخترع أي أرقام غير موجودة هنا.\n\n"
        f"الشهر: {month_label}\n"
        f"إجمالي الصرف: {total_spend:.2f} ريال\n"
        "الصرف حسب الفئة:\n" + _format_aggregate_lines(aggregate)
    )
    return _generate(prompt)


def answer_chat(aggregate: list[dict], message: str) -> str:
    """Answer a free-text question about the user's spending, in Arabic."""
    prompt = (
        "أنت مساعد مالي شخصي. أجب عن سؤال المستخدم بالعربية بإيجاز ودقة، "
        "بالاعتماد فقط على البيانات المجمّعة التالية. إن لم تكفِ البيانات للإجابة، قل ذلك بوضوح.\n\n"
        "بيانات الصرف حسب الفئة (كامل الفترة المتاحة):\n"
        + _format_aggregate_lines(aggregate)
        + f"\n\nسؤال المستخدم: {message}"
    )
    return _generate(prompt)
