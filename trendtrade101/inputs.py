"""Validate exact supplied files; never reconstruct or reselect a universe."""
from __future__ import annotations
import csv
import json
from collections import Counter
from pathlib import Path
from .storage import sha256, utcnow

EXPECTED = {
    "TrendTrade101_Backtest_Configuration.md": "2b1760c4db0339908e9facf6a73223c7071fe41200aebf0fbcfe8f6732f75de9",
    "frozen_universe_members.csv": "6441e090ca88ad8dd5d557b3cdbcca3d71971bec0c0070a750f67ca069a8e2b0",
    "frozen_universe_manifest.json": "3ee4c294809fe90619fe9eb06dbb110b53c6526ae21c47396a86f9a54a304b07",
    "frozen_universe_manifest.md": "7c4cee332c1e5b5d04f7e938c40bf30661cceb996fb997551a700e000e220af7",
}

class InputError(ValueError):
    pass

def verify(directory: Path) -> dict:
    checks, problems = [], []
    for name, expected in EXPECTED.items():
        p = directory / name
        actual = sha256(p) if p.is_file() else None
        ok = actual == expected
        checks.append({"name": name, "expected_sha256": expected, "actual_sha256": actual, "verified": ok})
        if not ok:
            problems.append(f"{name}: " + ("missing" if actual is None else "hash mismatch"))
    report = {"checked_at": utcnow(), "status": "blocked" if problems else "verified",
              "files": checks, "problems": problems, "membership_count": None, "unique_securities": None}
    if problems:
        return report
    with (directory / "frozen_universe_members.csv").open(newline="") as f:
        rows = list(csv.DictReader(f))
    manifest = json.loads((directory / "frozen_universe_manifest.json").read_text())
    groups = {}
    for row in rows:
        key = (row["market"], row["universe_id"], row["frequency"])
        groups.setdefault(key, []).append(row["ticker"])
    if len(rows) != 201 or len({(r["market"], r["ticker"]) for r in rows}) != 127:
        raise InputError("Expected 201 memberships and 127 distinct market/ticker pairs")
    for g in manifest["memberships"]:
        key = (g["market"], g["universe_id"], g["frequency"])
        tickers = groups.pop(key, None)
        if tickers != g["tickers_in_review_order"] or len(set(tickers or [])) != g["count"]:
            raise InputError(f"Membership/order mismatch: {key}")
    if groups:
        raise InputError("Unexpected membership group")
    daily = [r["ticker"] for r in rows if (r["market"], r["universe_id"], r["frequency"]) ==
             ("US", "historical_30_user_fixed", "daily")]
    if "NKE" in daily or daily[-1] != "PYPL":
        raise InputError("Approved PYPL exception is absent")
    report.update(membership_count=len(rows), unique_securities=127,
                  groups=manifest["memberships"], approved_exception="US daily: NKE to PYPL")
    return report

def require_verified(directory: Path) -> list[dict]:
    report = verify(directory)
    if report["status"] != "verified":
        raise InputError("; ".join(report["problems"]))
    with (directory / "frozen_universe_members.csv").open(newline="") as f:
        return list(csv.DictReader(f))

def symbols_for(rows: list[dict], market: str, universe: str, frequency: str) -> list[str]:
    return [r["ticker"] for r in rows if r["market"] == market and r["universe_id"] == universe
            and r["frequency"] in (frequency, "daily_and_5m")]
