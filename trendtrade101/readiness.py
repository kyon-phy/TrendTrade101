"""Fail-closed production run prerequisites."""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from .inputs import verify_project_inputs, EXPECTED
from .storage import read_json, utcnow
from .dashboard import result_catalog, research_progress

STAGES = ("inputs","canonical_sync","data_audit","holdout_freeze","baseline","optimization","final_holdout")

def provider_observation(*states: dict) -> dict:
    """Compare observation times, never file mtimes or software-test times."""
    observations=[]
    for state in states:
        provider=state.get("provider_preflight",{})
        if not provider:
            continue
        stamp=provider.get("observed_at",state.get("reported_at"))
        try:
            at=datetime.fromisoformat(stamp)
            if at.utcoffset() is None:
                raise ValueError("Naive observation time")
        except (ValueError,TypeError):
            at=datetime.min.replace(tzinfo=timezone.utc)
            stamp=None
        # Only observation summaries belong in the read-only public console.
        observation={k:provider[k] for k in ("status","message","http_status","failure_stage",
            "retry_after","limiting_layer","retry_policy","evidence") if k in provider}
        observation.update(observed_at=stamp,scope=provider.get("scope",state.get("scope","Unspecified")))
        observations.append((at,observation))
    return max(observations,key=lambda item:item[0])[1] if observations else {}

def status(root: Path) -> dict:
    config = read_json(root/"config/baseline.json",{})
    inputs = verify_project_inputs(root)
    public_state=read_json(root/"config/project_status.json",{})
    state = read_json(root/".private/status.json",{})
    provider = provider_observation(public_state,state)
    data_status="blocked" if provider.get("status") in ("blocked","failed") else "not_started"
    data_detail=provider.get("message","No complete verified-data audit. No vendor prices committed.")
    if provider and data_status!="blocked":
        data_detail+=" No complete verified-data audit; connectivity alone does not establish coverage."
    pending = config.get("pending",[])
    stages = [
        {"id":"inputs","name":"Frozen inputs","status":"complete" if inputs["status"]=="verified" else "blocked",
         "detail":("Public-derived bytes, provenance and ordered memberships verified; original Library bytes not verified."
                   if inputs["verification_kind"]=="public_derived" else "Original source bytes and ordered memberships verified")
                   if inputs["status"]=="verified" else "; ".join(inputs["problems"])},
        {"id":"canonical_sync","name":"Configuration synchronization",
         "status":"complete" if config.get("canonical_definitions_synchronized") and config.get("source_sha256")==EXPECTED["TrendTrade101_Backtest_Configuration.md"] else "blocked",
         "detail":"Accepted v0.13 execution/scoring definitions reconciled; remaining technical conventions are listed below."},
        {"id":"data_audit","name":"Market data audit","status":data_status,"detail":data_detail},
        {"id":"holdout_freeze","name":"Holdout reservation","status":"not_started",
         "detail":"Last complete week/month policy retained; exact audited dates pending."},
        {"id":"baseline","name":"Fixed baseline","status":"not_started","detail":"Real-data execution locked."},
        {"id":"optimization","name":"Walk-forward research","status":"not_started","detail":"Baseline must precede candidate selection."},
        {"id":"final_holdout","name":"Final holdout","status":"sealed","detail":"No final-holdout returns have been computed."},
    ]
    runs=research_progress(root)
    if runs:
        stages[2].update(status="in_progress",detail=f"Audited local packages supplied for {len(runs)} run(s); see per-run state.")
        stages[3].update(status="in_progress",detail=f"Exact final windows frozen for {len(runs)} run(s).")
        for index,field in ((4,"baseline_complete"),(5,"walk_forward_complete")):
            count=sum(r[field] for r in runs)
            if count:
                stages[index].update(status="in_progress",detail=f"Complete for {count} run(s); requested markets/baskets remain separately tracked.")
        consumed=sum(r["holdout_consumed"] for r in runs)
        if consumed:
            stages[6].update(status="in_progress",detail=f"Final sample consumed for {consumed} run(s); reuse prohibited.")
    return {"project":"TrendTrade101","version":config.get("source_version"),
            "updated_at":utcnow(),"run_status":"blocked","stages":stages,"inputs":inputs,
            "pending":pending,"biases":config.get("biases",[]),
            "accepted_pending_canonical_sync":config.get("accepted_pending_canonical_sync",[]),
            "accepted_definitions":config.get("accepted_definitions",[]),
            "parameters":{"indicators":config.get("indicators",{}),"execution":config.get("execution",{}),
                          "markets":config.get("markets",{}),"research":config.get("research",{})},
            "provider_preflight":provider,
            "verification":state.get("verification",{}),"results":result_catalog(root),"runs":runs,
            "access":{"mode":"read_only","data":"No raw vendor data is exposed."}}

def require_ready(root: Path):
    snapshot = status(root)
    problems = [s["detail"] for s in snapshot["stages"][:4] if s["status"]!="complete"]
    if problems:
        raise RuntimeError("Run blocked: "+" | ".join(problems))
