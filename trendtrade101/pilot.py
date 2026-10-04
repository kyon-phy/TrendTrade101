"""Isolated existing-25 daily baseline pilot; no tuning or holdout consumption."""
from __future__ import annotations
from dataclasses import replace
from datetime import date,datetime,timedelta
from pathlib import Path
import subprocess
from .dataset import PILOT_KIND,PILOT_SCOPE,Dataset,fingerprint
from .inputs import EXPECTED,project_members,symbols_for,verify_project_inputs
from .orchestration import _segment,_validate_accounting,implementation_digest,midnight
from .research import Interval
from .storage import read_json,write_json,utcnow

PILOT_CONVENTIONS={
    "indicator_initialization":"sma_seeded_ema_wilder_adx",
    "signal_gap_policy":"observed_valid_bars_no_fill",
    "valuation_cadence":"observed_open_close_and_scheduled_events",
    "partial_window_policy":"whole_calendar_months_prior_history_warmup_only",
}

def private_directory(root:Path,directory:Path,*,runs=False):
    base=(root/".private"/("pilots" if runs else "")).resolve()
    target=directory.resolve()
    if not target.is_relative_to(base) or target==base:
        raise ValueError("Pilot output must be a child of "+str(base))

def _settings(root:Path,dataset:Dataset):
    if dataset.kind not in (PILOT_KIND,"synthetic_pilot_fixture") or dataset.frequency!="daily":
        raise ValueError("Use a dedicated existing-25 daily pilot dataset")
    if dataset.manifest.get("research_scope")!=PILOT_SCOPE:
        raise ValueError("Pilot dataset scope mismatch")
    config=read_json(root/"config/baseline.json")
    pilot=read_json(root/"config/daily_pilot.json")
    if not pilot or pilot.get("scope_approval")!="recorded" or pilot.get("research_scope")!=PILOT_SCOPE:
        raise ValueError("Awaiting the synchronized canonical pilot scope; no effective run is enabled")
    if pilot.get("source_sha256")!=EXPECTED["TrendTrade101_Backtest_Configuration.md"] or (
        pilot.get("source_sha256")!=config.get("source_sha256") or pilot.get("source_version")!=config.get("source_version")):
        raise ValueError("Pilot configuration is not synchronized with canonical inputs")
    if pilot.get("technical_conventions")!=PILOT_CONVENTIONS:
        raise ValueError("Pilot technical conventions require canonical synchronization and verification")
    if not pilot.get("execution_ready"):
        raise ValueError("Pilot execution remains locked pending configuration and data verification")
    members=symbols_for(project_members(root),dataset.market,"existing_25","daily")
    if set(members)!=set(dataset.manifest["members"]):
        raise ValueError("Pilot must preserve every existing-25 constituent in its market")
    _validate_accounting(config,dataset,members)
    if any(config["execution"][key]["enabled"] for key in ("price_stop","price_target")):
        raise ValueError("Pilot uses the approved baseline without finite price exits")
    bounds=pilot.get("interval") or {}
    start,end=date.fromisoformat(bounds["start"]),date.fromisoformat(bounds["end"])
    protected=date.fromisoformat(pilot["protected_from"])
    if start.day!=1 or end.day!=1 or start>=end or end>protected:
        raise ValueError("Pilot interval must contain whole months before the protected boundary")
    if date.fromisoformat(dataset.manifest["calendar_complete_from"])>start or (
        date.fromisoformat(dataset.manifest["calendar_complete_through"])<end-timedelta(days=1)):
        raise ValueError("Calendar does not cover the entire pilot interval")
    if datetime.fromisoformat(dataset.manifest["study_start"])!=midnight(start,dataset.manifest["timezone"]):
        raise ValueError("Audited pilot start differs from the canonical interval")
    # If formal research has already frozen a stricter boundary, do not explore it.
    for folder in (root/".private/runs").glob("*"):
        formal=read_json(folder/"plan.json")
        if formal and formal.get("market")==dataset.market and formal.get("frequency")=="daily":
            if end>date.fromisoformat(formal["holdout"]["start"]):
                raise ValueError("Pilot would overlap an already reserved formal holdout")
    if dataset.kind==PILOT_KIND and verify_project_inputs(root)["status"]!="verified":
        raise ValueError("Canonical/public input verification must pass before a real pilot")
    return config,pilot,members,Interval(start,end)

def _code_receipt(root:Path,dataset:Dataset):
    if dataset.kind=="synthetic_pilot_fixture":return {"commit":None,"scope":"synthetic_test_only"}
    def git(*args):
        return subprocess.check_output(["git","-C",str(root),*args],text=True).strip()
    if git("status","--porcelain"):
        raise ValueError("Commit reviewed implementation/configuration before freezing a real pilot")
    return {"commit":git("rev-parse","HEAD"),"working_tree_dirty":False}

def freeze_pilot(root:Path,dataset:Dataset,run_dir:Path):
    private_directory(root,run_dir,runs=True)
    config,pilot,members,interval=_settings(root,dataset)
    begin,end=midnight(interval.start,dataset.manifest["timezone"]),midnight(interval.end,dataset.manifest["timezone"])
    coverage={}
    for ticker in members:
        history=sorted((b for b in dataset.bars if b.ticker==ticker and b.end<end),key=lambda b:b.start)
        warmup=[b for b in history if b.end<begin]
        scored=[b for b in history if b.start>=begin]
        bounds=lambda bars:{"bars":len(bars),"first":bars[0].start.isoformat() if bars else None,
                            "last":bars[-1].end.isoformat() if bars else None}
        coverage[ticker]={"warmup":bounds(warmup),"scored":bounds(scored),
            "availability":dataset.manifest["members"][ticker]["availability"],
            "first_trade_date":dataset.manifest["members"][ticker].get("first_trade_date")}
    plan={"schema_version":1,"research_scope":PILOT_SCOPE,"created_at":utcnow(),
        "dataset_kind":dataset.kind,"dataset_digest":dataset.digest,
        "configuration_digest":fingerprint(config),"pilot_configuration_digest":fingerprint(pilot),
        "configuration_version":config["source_version"],"configuration_source_sha256":config["source_sha256"],
        "implementation_digest":implementation_digest(),"code":_code_receipt(root,dataset),
        "market":dataset.market,"frequency":"daily","universe":"existing_25",
        "timezone":dataset.manifest["timezone"],"members":members,"allocation":"fixed",
        "coverage":coverage,
        "interval":{"start":interval.start.isoformat(),"end":interval.end.isoformat()},
        "protected_from":pilot["protected_from"],"formal_holdout_consumed":False,
        "optimization_permitted":False,"arms":["FULL"],
        "baseline":{k:config["indicators"][k] for k in ("adx_threshold","cross_window","hist_drawdown")},
        "delay_minutes":config["execution"]["delay_minutes"],
        "account_state":config["account_state"],"corporate_actions":config["corporate_actions"],
        "biases":config["biases"]+[
            "Exploratory daily pilot on the existing-25 cached subset; not the formal five-year study.",
            "No parameter optimization or final-holdout evaluation. Later formal holdouts must exclude this explored interval.",
            "Observed cache depth is not maximum available history; late IPOs and startup gaps shorten effective participation."]}
    existing=read_json(run_dir/"plan.json")
    if existing:
        comparable=lambda p:{k:v for k,v in p.items() if k!="created_at"}
        if comparable(existing)!=comparable(plan):raise ValueError("Frozen pilot plan differs")
        return existing
    write_json(run_dir/"plan.json",plan)
    write_json(run_dir/"progress.json",{"stage":"pilot_plan_frozen","dataset_kind":dataset.kind,"updated_at":utcnow()})
    return plan

def run_pilot(root:Path,dataset:Dataset,run_dir:Path):
    private_directory(root,run_dir,runs=True)
    config,pilot,members,interval=_settings(root,dataset)
    plan=read_json(run_dir/"plan.json")
    if not plan or plan.get("research_scope")!=PILOT_SCOPE:raise ValueError("Freeze a pilot plan first")
    # Reconstruct the whole expected plan, including all arms and baseline values.
    freeze_pilot(root,dataset,run_dir)
    if (plan["dataset_digest"]!=dataset.digest or plan["configuration_digest"]!=fingerprint(config)
        or plan["pilot_configuration_digest"]!=fingerprint(pilot)
        or plan["implementation_digest"]!=implementation_digest() or plan["code"]!=_code_receipt(root,dataset)):
        raise ValueError("Frozen pilot data/configuration/code changed")
    if plan["members"]!=members or plan["interval"]!={"start":interval.start.isoformat(),"end":interval.end.isoformat()}:
        raise ValueError("Frozen pilot scope changed")
    if (run_dir/"baseline-complete.json").exists():raise ValueError("Pilot baseline is already complete")
    end=midnight(interval.end,plan["timezone"])
    # Remove the protected observations entirely, even from the replay event grid.
    bounded=replace(dataset,bars=[b for b in dataset.bars if b.end<end],
        open_quotes=[q for q in dataset.open_quotes if q.start<end],
        sessions=[s for s in dataset.sessions if s.end<end],
        manifest={**dataset.manifest,"splits":[a for a in dataset.manifest.get("splits",[])
                                              if datetime.fromisoformat(a["at"])<end]})
    if not any(b.start>=midnight(interval.start,plan["timezone"]) for b in bounded.bars):
        raise ValueError("No observed bars in the approved pilot scoring interval")
    outputs={}
    for i,arm in enumerate(plan["arms"]):
        write_json(run_dir/"progress.json",{"stage":"pilot_baseline","arm":arm,"completed":i,
            "total":len(plan["arms"]),"dataset_kind":dataset.kind,"updated_at":utcnow()})
        result,_=_segment(config,bounded,plan,arm,plan["baseline"],interval)
        result.update(phase="exploratory_daily_pilot",research_scope=PILOT_SCOPE,
            formal_holdout_consumed=False,optimization_permitted=False,protected_from=plan["protected_from"],
            plan_digest=fingerprint(plan),code=plan["code"],coverage=plan["coverage"],
            execution_outcome=("completed_closures" if result["metrics"]["closed_trades"] else
                               "residual_positions" if result["residual_positions"] else "cash_only_no_completed_closures"))
        result["limitations"]+=plan["biases"][-3:]
        write_json(run_dir/"baseline"/(arm+".json"),result)
        outputs[arm]=result["metrics"]
    write_json(run_dir/"baseline-complete.json",{"research_scope":PILOT_SCOPE,"plan_digest":fingerprint(plan),
        "dataset_digest":dataset.digest,"arms":plan["arms"],"completed_at":utcnow()})
    write_json(run_dir/"progress.json",{"stage":"pilot_complete","dataset_kind":dataset.kind,"updated_at":utcnow()})
    return outputs
