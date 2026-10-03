"""Fail-closed production run prerequisites."""
from __future__ import annotations
from pathlib import Path
from .inputs import verify
from .storage import read_json, utcnow

STAGES = ("inputs","canonical_sync","data_audit","holdout_freeze","baseline","optimization","final_holdout")

def status(root: Path) -> dict:
    config = read_json(root/"config/baseline.json",{})
    inputs = verify(root/".private/inputs")
    state = read_json(root/".private/status.json",{})
    pending = config.get("pending",[])
    stages = [
        {"id":"inputs","name":"Frozen inputs","status":"complete" if inputs["status"]=="verified" else "blocked",
         "detail":"Exact bytes and ordered memberships verified" if inputs["status"]=="verified" else "; ".join(inputs["problems"])},
        {"id":"canonical_sync","name":"Configuration synchronization","status":"blocked",
         "detail":"Accepted execution/scoring decisions await a guarded update of the canonical configuration."},
        {"id":"data_audit","name":"Market data audit","status":"not_started",
         "detail":"No complete verified-data audit. No vendor prices committed."},
        {"id":"holdout_freeze","name":"Holdout reservation","status":"not_started",
         "detail":"Last complete week/month policy retained; exact audited dates pending."},
        {"id":"baseline","name":"Fixed baseline","status":"not_started","detail":"Real-data execution locked."},
        {"id":"optimization","name":"Walk-forward research","status":"not_started","detail":"Baseline must precede candidate selection."},
        {"id":"final_holdout","name":"Final holdout","status":"sealed","detail":"No final-holdout returns have been computed."},
    ]
    return {"project":"TrendTrade101","version":config.get("source_version"),
            "updated_at":utcnow(),"run_status":"blocked","stages":stages,"inputs":inputs,
            "pending":pending,"biases":config.get("biases",[]),
            "accepted_pending_canonical_sync":config.get("accepted_pending_canonical_sync",[]),
            "parameters":{"indicators":config.get("indicators",{}),"execution":config.get("execution",{}),
                          "markets":config.get("markets",{}),"research":config.get("research",{})},
            "verification":state.get("verification",{}),"results":[],
            "access":{"mode":"read_only","data":"No raw vendor data is exposed."}}

def require_ready(root: Path):
    snapshot = status(root)
    problems = [s["detail"] for s in snapshot["stages"][:4] if s["status"]!="complete"]
    if problems:
        raise RuntimeError("Run blocked: "+" | ".join(problems))
