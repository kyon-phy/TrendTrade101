"""Free read-only Yahoo chart capture. No fallback hosts or proxy bypasses."""
from __future__ import annotations
import hashlib
import json
import urllib.parse
import urllib.request
from pathlib import Path
from .storage import utcnow, write_json

def capture(ticker: str, interval: str, directory: Path, *, query: dict) -> dict:
    if interval not in ("5m", "1d", "1m", "1h"):
        raise ValueError("Unsupported interval")
    params = {**query, "interval":interval, "events":"div,splits", "includePrePost":"false"}
    url = "https://query1.finance.yahoo.com/v8/finance/chart/" + urllib.parse.quote(ticker, safe="") + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"User-Agent":"TrendTrade101/0.1 research"})
    started = utcnow()
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read()
        payload = json.loads(raw)
        if payload.get("chart",{}).get("error"):
            raise ValueError(str(payload["chart"]["error"]))
    except Exception as exc:
        # Stop at the original endpoint; never evade a denied request.
        return {"status":"failed", "ticker":ticker, "interval":interval,
                "request":params, "retrieved_at":started, "error":str(exc)}
    digest = hashlib.sha256(raw).hexdigest()
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    destination = directory / (digest + ".json")
    if not destination.exists():
        destination.write_bytes(raw)
        destination.chmod(0o600)
    record = {"status":"captured", "ticker":ticker, "interval":interval,
              "request":params, "retrieved_at":started, "sha256":digest,
              "size_bytes":len(raw), "file":destination.name}
    write_json(directory / (digest + ".metadata.json"), record)
    return record
