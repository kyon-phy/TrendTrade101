"""Free read-only Yahoo chart capture. No fallback hosts or proxy bypasses."""
from __future__ import annotations
import hashlib
import json
import urllib.error
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
    failure_stage="connection_before_response"
    def failed(exc,**details):
        return {"status":"failed","ticker":ticker,"interval":interval,"request":params,
                "retrieved_at":started,"error":str(exc),"failure_stage":failure_stage,
                "retry_policy":"stop_no_automatic_retry",**details}
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            failure_stage="response_read"
            raw = response.read()
        failure_stage="response_validation"
        payload = json.loads(raw)
        if payload.get("chart",{}).get("error"):
            raise ValueError(str(payload["chart"]["error"]))
    except urllib.error.HTTPError as exc:
        # Bounded diagnostics only. An HTTP response is distinct from a CONNECT
        # failure, but neither the status nor Server identifies the limiting layer.
        details={"failure_stage":"http_response_before_json","http_status":exc.code,
                 "server":exc.headers.get("Server") if exc.headers else None,
                 "retry_after":exc.headers.get("Retry-After") if exc.headers else None,
                 "limiting_layer":"unknown"}
        try:
            preview=exc.read(4096)
            details.update(response_preview=preview.decode("utf-8",errors="replace")[:200],
                           response_preview_bytes=len(preview),response_preview_limit=4096,
                           response_preview_sha256=hashlib.sha256(preview).hexdigest())
        except OSError:
            details["response_preview_unavailable"]=True
        finally:
            exc.close()
        return failed(exc,**details)
    except Exception as exc:
        # Stop at the original endpoint; never evade a denied request.
        return failed(exc)
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
