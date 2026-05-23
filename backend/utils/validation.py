from typing import Dict, Any, Tuple, List

ALERT_RULES = [
    {"category": "high_latency", "threshold": 1500, "severity": "medium", "message": "Latency above expected threshold."},
    {"category": "failed_execution", "threshold": 1, "severity": "high", "message": "Workflow execution failed."},
]

def validate_workflow_payload(payload: Dict[str, Any]) -> Tuple[bool, List[Dict[str, Any]]]:
    errors = []
    if not payload.get("name"):
        errors.append({"field": "name", "message": "Workflow name is required."})
    if not payload.get("type"):
        errors.append({"field": "type", "message": "Workflow type is required."})
    return (len(errors) == 0, errors)


def generate_alerts(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    alerts = []
    latency = int(payload.get("latency_ms", 0) or 0)
    status = payload.get("status", "pending")
    for rule in ALERT_RULES:
        if rule["category"] == "high_latency" and latency >= rule["threshold"]:
            alerts.append({
                "severity": rule["severity"],
                "message": rule["message"],
                "category": rule["category"],
            })
        if rule["category"] == "failed_execution" and status == "failed":
            alerts.append({
                "severity": rule["severity"],
                "message": rule["message"],
                "category": rule["category"],
            })
    return alerts


def validate_market_response(asset: str, price: Any, latency_ms: int, status: Any) -> Dict[str, Any]:
    """Validate a market snapshot and return structured issue info.

    Returns dict with keys: severity (ok/low/medium/high/critical), message, category
    """
    # default ok
    result = {"severity": "ok", "message": "ok", "category": "market"}

    # failed request
    if status != 200:
        result.update({"severity": "high", "message": f"API request failed with status {status}", "category": "reliability"})
        return result

    # missing price
    if price is None:
        result.update({"severity": "critical", "message": "missing market data", "category": "validation"})
        return result

    # non-numeric
    try:
        float(price)
    except Exception:
        result.update({"severity": "critical", "message": "invalid numeric value for price", "category": "validation"})
        return result

    # latency thresholds
    if latency_ms > 500:
        result.update({"severity": "medium", "message": "latency above 500ms", "category": "latency"})
    elif latency_ms > 200:
        result.update({"severity": "low", "message": "latency above 200ms", "category": "latency"})

    return result


def severity_from_code(code: str) -> str:
    mapping = {"ok": "low", "low": "low", "medium": "medium", "high": "high", "critical": "critical"}
    return mapping.get(code, "low")
