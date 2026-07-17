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
        "بالاعتماد فقط على البيانات المجمّعة التالية. لا تخترع أي أرقام غير موجودة هنا. "
        "لا تستخدم الرموز التعبيرية (emoji).\n\n"
        f"الشهر: {month_label}\n"
        f"إجمالي الصرف: {total_spend:.2f} ريال\n"
        "الصرف حسب الفئة:\n" + _format_aggregate_lines(aggregate)
    )
    return _generate(prompt)


def _format_context(ctx: dict) -> str:
    parts: list[str] = []
    parts.append(f"إجمالي الصرف: {ctx['total_spend']:.2f} ريال")
    parts.append(f"إجمالي الدخل: {ctx['total_income']:.2f} ريال")

    parts.append("\nالصرف حسب الفئة (كامل الفترة):")
    parts.append(_format_aggregate_lines(ctx["by_category"]))

    parts.append("\nالصرف حسب الشهر:")
    parts.append("\n".join(f"- {m['month']}: {m['total']:.2f} ريال" for m in ctx["by_month"]))

    parts.append("\nالصرف لكل شهر حسب الفئة:")
    for month, items in ctx["by_month_category"].items():
        line = "، ".join(f"{it['category']} {it['total']:.0f}" for it in items)
        parts.append(f"- {month}: {line}")

    if ctx["top_merchants"]:
        parts.append("\nأعلى المتاجر إنفاقًا:")
        parts.append(
            "\n".join(
                f"- {m['name']}: {m['total']:.2f} ريال ({m['count']} عملية)"
                for m in ctx["top_merchants"]
            )
        )
    return "\n".join(parts)


def answer_chat(context: dict, message: str) -> str:
    """Answer a free-text question about the user's spending, in Arabic.

    ``context`` is the rich, already-aggregated grounding from the repository
    (totals, per-category, per-month, per-month-per-category, top merchants).
    """
    prompt = (
        "أنت مساعد مالي شخصي ذكي تتحدث بالعربية. أجب عن سؤال المستخدم بإيجاز ووضوح، "
        "مستعيناً بالبيانات المجمّعة التالية عن إنفاقه. يمكنك: مقارنة الأشهر، تحليل الفئات، "
        "تحديد أعلى المصاريف، وتقديم نصائح عملية للتوفير مبنية على هذه الأرقام. "
        "استخدم الأرقام الفعلية من البيانات، ونسّق إجابتك بنقاط عند الحاجة (استخدم ** للتأكيد). "
        "لا تستخدم الرموز التعبيرية (emoji) نهائياً. "
        "لا تخترع أرقاماً أو أسماء غير موجودة. اعتذر فقط إذا كان السؤال خارج نطاق البيانات تماماً.\n\n"
        "== بيانات المستخدم ==\n"
        + _format_context(context)
        + f"\n\nسؤال المستخدم: {message}"
    )
    return _generate(prompt)
