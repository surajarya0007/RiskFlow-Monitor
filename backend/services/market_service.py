import asyncio
import time
import logging
from typing import Dict, Any
import aiohttp
from backend.config import settings
from backend.websocket.manager import manager
from backend.services.log_service import create_log
from backend.services.workflow_service import create_workflow
from backend.services.alert_service import create_alert
from backend.db.base import get_pool
from backend.utils.validation import validate_market_response, severity_from_code

logger = logging.getLogger(__name__)


def build_coingecko_url() -> str:
    params = "vs_currencies=usd&ids=bitcoin,ethereum,solana"
    if settings.COINGECKO_API_KEY:
        params += f"&x_cg_demo_api_key={settings.COINGECKO_API_KEY}"
    return f"{settings.COINGECKO_BASE_URL}?{params}"


async def fetch_market_snapshot(session: aiohttp.ClientSession) -> Dict[str, Any]:
    start = time.perf_counter()
    url = build_coingecko_url()
    try:
        async with session.get(url, timeout=10) as resp:
            latency_ms = int((time.perf_counter() - start) * 1000)
            status = resp.status
            data = await resp.json()
            return {"status": status, "latency_ms": latency_ms, "data": data}
    except Exception as e:
        latency_ms = int((time.perf_counter() - start) * 1000)
        logger.exception("Market fetch failed")
        return {"status": "error", "latency_ms": latency_ms, "data": None, "error": str(e)}


async def persist_market_snapshot(asset: str, price: float, latency_ms: int, status: str):
    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO market_data (asset, price_usd, latency_ms, request_status) VALUES ($1, $2, $3, $4)",
            asset,
            price,
            latency_ms,
            str(status),
        )


async def run_market_monitor(poll_interval: float = 5.0):
    async with aiohttp.ClientSession() as session:
        while True:
            snapshot = await fetch_market_snapshot(session)
            ts = snapshot.get("latency_ms", 0)
            status = snapshot.get("status")
            data = snapshot.get("data")

            # validate and create workflows/alerts/logs per asset
            if data:
                for asset_key in ["bitcoin", "ethereum", "solana"]:
                    asset_info = data.get(asset_key)
                    if asset_info and isinstance(asset_info, dict):
                        price = asset_info.get("usd")
                        await persist_market_snapshot(asset_key, price, ts, status)

                        display_asset = asset_key.capitalize()
                        workflow_name = f"Market Data Sync ({display_asset})"

                        # validation
                        issues = validate_market_response(asset_key, price, ts, status)

                        # create workflow based on validation outcome
                        if issues["severity"] == "ok":
                            workflow = await create_workflow({
                                "name": workflow_name,
                                "type": "Market Data Sync",
                                "status": "completed",
                                "latency_ms": ts,
                                "metadata": {"asset": asset_key, "price": price},
                            })
                            await create_log({
                                "workflow_id": workflow["id"],
                                "event_type": "market.snapshot",
                                "metadata": {"asset": asset_key, "price": price, "latency_ms": ts},
                            })
                            await manager.broadcast({"type": "workflow.created", "item": workflow})
                        else:
                            # map severity -> workflow
                            wf_type = "API Reliability Monitor" if issues["severity"] == "medium" else "Risk Validation"
                            wf_status = "warning" if issues["severity"] == "medium" else "failed"
                            workflow = await create_workflow({
                                "name": f"{wf_type} ({display_asset})",
                                "type": wf_type,
                                "status": wf_status,
                                "latency_ms": ts,
                                "metadata": {"asset": asset_key, "issues": issues},
                            })
                            # create alert
                            alert_payload = {
                                "severity": issues["severity"],
                                "message": issues.get("message", "market validation issue"),
                                "category": issues.get("category", "validation"),
                            }
                            await create_alert(workflow.get("id"), alert_payload)
                            await create_log({
                                "workflow_id": workflow["id"],
                                "event_type": "market.validation",
                                "metadata": {"asset": asset_key, "issues": issues},
                            })
                            await manager.broadcast({"type": "workflow.created", "item": workflow})
            else:
                # global failure
                logger.warning("Market fetch returned no data: %s", snapshot.get("error"))

            # also broadcast raw market snapshot to clients
            await manager.broadcast({"type": "market.snapshot", "item": snapshot})

            await asyncio.sleep(poll_interval)
