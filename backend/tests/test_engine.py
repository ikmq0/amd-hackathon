"""Engine behavior tests — the guarantees we demo."""

from __future__ import annotations

import pytest

from app.engine.cleaner import clean
from app.engine.pipeline import DecodingEngine
from app.repositories.merchant_repo import build_repo
from app.schemas import Category, ResolvedBy


@pytest.fixture(scope="module")
def engine() -> DecodingEngine:
    return DecodingEngine(build_repo())


@pytest.mark.parametrize(
    "raw,merchant_id,category",
    [
        ("MCD_2938_RYD*SP", "mcd", Category.RESTAURANT),
        ("JAHEZ*DLVR_88_APP", "jahez", Category.FOOD_DELIVERY),
        ("PANDA_HYPER_2213", "panda", Category.GROCERY),
        ("INMA_E_PAY_9482", "alinma", Category.TRANSFER),
        ("NOON*ECOM_SA_4491", "noon", Category.SHOPPING),
        ("STCPAY_TOPUP_09", "stcpay", Category.TELECOM),
        ("AMZNMKTP_SA_71", "amazon", Category.SHOPPING),
    ],
)
def test_exact_resolution(engine, raw, merchant_id, category):
    r = engine.decode(raw)
    assert r.resolved is True
    assert r.merchant_id == merchant_id
    assert r.category == category
    assert 0.0 <= r.confidence <= 1.0


def test_arabic_alias_resolves(engine):
    r = engine.decode("جرير_الرياض_44")
    assert r.merchant_id == "jarir"
    assert r.city == "الرياض"


def test_unknown_is_explicit_not_a_guess(engine):
    r = engine.decode("ZZZ_9999_XX")
    assert r.resolved is False
    assert r.merchant is None and r.merchant_id is None
    assert r.category == Category.OTHER
    assert r.resolved_by == ResolvedBy.UNKNOWN
    assert r.confidence == 0.0


def test_city_extraction_from_code(engine):
    assert engine.decode("MCD_2938_JED").city == "جدة"
    assert engine.decode("MCD_2938_DMM").city == "الدمام"


def test_arabic_indic_digits_are_normalized():
    cleaned = clean("PANDA_٢٢١٣_RUH")
    assert "PANDA" in cleaned.tokens
    assert cleaned.city_code == "RUH"


def test_cache_hit_on_repeat(engine):
    before = engine.cache.hits
    engine.decode("KFC_1111_RUH")
    engine.decode("KFC_2222_JED")  # same normalized concat -> cache hit
    assert engine.cache.hits > before


def test_closed_set_only_returns_known_ids(engine):
    r = engine.decode("HERFY_0007_RUH")
    assert r.merchant_id in engine.repo.by_id
