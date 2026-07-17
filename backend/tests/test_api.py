"""API smoke tests — lifespan seeds SQLite, then every route is exercised."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:  # triggers lifespan (build engine + seed DB)
        yield c


def test_health(client):
    assert client.get("/health").json()["status"] == "ok"


def test_decode_single(client):
    d = client.post("/decode", json={"raw": "MCD_2938_RYD*SP"}).json()
    assert d["merchant"] == "ماكدونالدز"
    assert d["category"] == "RESTAURANT"
    assert d["resolved"] is True


def test_decode_unknown_never_guesses(client):
    d = client.post("/decode", json={"raw": "ZZZQ_0000_XX"}).json()
    assert d["resolved"] is False
    assert d["merchant"] is None


def test_decode_batch(client):
    body = {"items": [{"raw": "JAHEZ_88"}, {"raw": "PANDA_1"}, {"raw": "NOON_SA_9"}]}
    out = client.post("/decode/batch", json=body).json()
    assert [x["merchant_id"] for x in out] == ["jahez", "panda", "noon"]


def test_transactions_seeded(client):
    rows = client.get("/transactions").json()
    assert len(rows) == 150
    assert {"name", "raw", "cat", "city", "date", "amt", "acc"} <= rows[0].keys()


def test_transactions_filter(client):
    rows = client.get("/transactions", params={"category": "مطاعم"}).json()
    assert rows and all(r["cat"] == "مطاعم" for r in rows)


def test_merchants_and_analytics(client):
    assert client.get("/merchants").json()
    assert client.get("/analytics/breakdown").json()
    assert len(client.get("/analytics/monthly").json()) >= 1
    assert len(client.get("/analytics/accuracy").json()) >= 1


def test_stats_shape(client):
    s = client.get("/stats").json()
    assert s["tx_count"] == 150
    assert 0 <= s["accuracy_pct"] <= 100
    assert "resolved_by" in s
