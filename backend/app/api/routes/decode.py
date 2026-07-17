"""Decode endpoints — the core product surface.

Batch is primary (Open Banking delivers statements); single is batch-of-one.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_decoder, require_api_key
from app.engine.pipeline import DecodingEngine
from app.schemas import BatchDecodeRequest, DecodeRequest, DecodeResult

router = APIRouter(prefix="/decode", tags=["decode"], dependencies=[Depends(require_api_key)])


@router.post("", response_model=DecodeResult)
async def decode_one(
    body: DecodeRequest, decoder: DecodingEngine = Depends(get_decoder)
) -> DecodeResult:
    return decoder.decode(body.raw)


@router.post("/batch", response_model=list[DecodeResult])
async def decode_batch(
    body: BatchDecodeRequest, decoder: DecodingEngine = Depends(get_decoder)
) -> list[DecodeResult]:
    return decoder.decode_batch(body.items)
