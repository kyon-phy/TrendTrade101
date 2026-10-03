"""Baseline-first, causal research against verified local dataset packages."""
from __future__ import annotations
from dataclasses import asdict
from datetime import date,datetime,timedelta,time
import json
import os
from pathlib import Path
from zoneinfo import ZoneInfo
from .dataset import Dataset,fingerprint,load_dataset
from .engine import replay
from .inputs import project_members,symbols_for
from .portfolio import Ledger,LedgerPolicy
from .research import Interval,candidates,folds,guard_training,holdout_from_complete_sessions,select_candidate
from .schedule import liquidation_schedule
from .reporting import summarize
from .signals import SignalRules
from .storage import read_json,write_json,utcnow

def implementation_digest():
    return fingerprint({p.name:p.read_text() for p in sorted(Path(__file__).parent.glob("*.py"))})

def midnight(d,timezone):
    return datetime.combine(d,time.min,tzinfo=ZoneInfo(timezone))

def freeze_plan(root: Path, dataset: Dataset, universe: str, run_dir: Path) -> dict:
    config=read_json(root/"config/baseline.json")
    members=symbols_for(project_members(root),dataset.market,universe,dataset.frequency)
    if not members: raise ValueError("Unknown/empty universe")
    complete=[date.fromisoformat(x) for x in dataset.manifest["complete_session_dates"]]
    period_ends={date.fromisoformat(x) for x in dataset.manifest["complete_period_ends"]}
    holdout=holdout_from_complete_sessions(complete,frequency=dataset.frequency,
        as_of=date.fromisoformat(dataset.manifest["as_of_date"]),audited_period_ends=period_ends)
    first=min(b.start.astimezone(ZoneInfo(dataset.manifest["timezone"])).date()
              for b in dataset.bars)
    windows=list(folds(first,holdout,frequency=dataset.frequency))
    if not windows: raise ValueError("Insufficient pre-holdout history for a full training/test fold")
    plan={"schema_version":1,"created_at":utcnow(),"dataset_digest":dataset.digest,
          "dataset_kind":dataset.kind,"configuration_digest":fingerprint(config),
          "implementation_digest":implementation_digest(),
          "configuration_version":config["source_version"],"market":dataset.market,
          "frequency":dataset.frequency,"timezone":dataset.manifest["timezone"],
          "universe":universe,"members":members,"allocation":"fixed",
          "baseline":{k:config["indicators"][k] for k in ("adx_threshold","cross_window","hist_drawdown")},
          "delay_minutes":config["execution"]["delay_minutes"],
          "holdout":{"start":holdout.start.isoformat(),"end":holdout.end.isoformat()},
          "folds":[{"train":{"start":a.start.isoformat(),"end":a.end.isoformat()},
                    "test":{"start":b.start.isoformat(),"end":b.end.isoformat()}} for a,b in windows],
          "objective":"after_tax_return","neighborhood":"axis_adjacent_median",
          "parameter_tie_order":["adx_threshold","cross_window","hist_drawdown"],
          "valuation_cadence":"Every observed bar Open and Close and scheduled event; missing observations retain last observable marks.",
          "partial_window_policy":"Require full calendar training and test windows; exclude partial leading/trailing periods.",
          "initial_position_policy":"Flat at each training start; retain cash and residual positions across ordinary OOS folds.",
          "sparse_trade_threshold":5,"minimum_trade_count_filter":None,
          "biases":config["biases"],"final_holdout_reuse":False}
    current=read_json(run_dir/"plan.json")
    if current:
        comparable=lambda p:{k:v for k,v in p.items() if k!="created_at"}
        if comparable(current)!=comparable(plan):
            raise ValueError("Existing frozen plan differs; create a distinct research round")
        return current
    write_json(run_dir/"plan.json",plan)
    write_json(run_dir/"progress.json",{"stage":"plan_frozen","dataset_kind":dataset.kind,"updated_at":utcnow()})
    return plan

def _interval(v):return Interval(date.fromisoformat(v["start"]),date.fromisoformat(v["end"]))

def _check(root,dataset,plan):
    config=read_json(root/"config/baseline.json")
    if dataset.digest!=plan["dataset_digest"] or fingerprint(config)!=plan["configuration_digest"]:
        raise ValueError("Frozen data/configuration no longer matches the research plan")
    if plan.get("implementation_digest")!=implementation_digest():
        raise ValueError("Implementation changed after the plan was frozen")
    if dataset.kind=="yahoo_audited" and not config.get("execution_ready"):
        raise ValueError("Real-data execution requires completed configuration/implementation verification")
    if any(config["execution"][name]["enabled"] for name in ("price_stop","price_target")):
        raise ValueError("Finite price exits require approved reference and trigger ordering")
    return config

def _ledger(config,dataset,plan):
    market=config["markets"][dataset.market]
    return Ledger(capital=market["capital"],position_cap=market["position_cap"],
        fee_rate=market["fee_rate"],fee_cap=market["fee_cap"],tax_rate=config["execution"]["annual_tax_rate"],
        lots={t:dataset.manifest["members"][t]["lot"] for t in plan["members"]},
        policy=LedgerPolicy(**config["ledger_policy"]))

def _segment(config,dataset,plan,arm,parameters,interval,ledger=None,allow_entries=True):
    ledger=ledger or _ledger(config,dataset,plan)
    bars=[b for b in dataset.bars if b.ticker in plan["members"]]
    events=liquidation_schedule(dataset.sessions,plan["members"],frequency=dataset.frequency,delay_minutes=plan["delay_minutes"])
    result=replay(bars,ledger=ledger,start=midnight(interval.start,plan["timezone"]),
        end=midnight(interval.end,plan["timezone"]),frequency=dataset.frequency,
        market_timezone=plan["timezone"],arm=arm,allocation="fixed",
        signal_rules=SignalRules(**config["signal_rules"]),seed_method="sma_seed",
        increments=config["indicators"]["hist_increments"],delay_minutes=plan["delay_minutes"],scaled_base=None,planned_exits=events,
        dataset_kind="synthetic" if dataset.kind=="synthetic_fixture" else "yahoo_audited",
        audit_digest=dataset.digest,allow_entries=allow_entries,
        splits=[a for a in dataset.manifest.get("splits",[]) if a["ticker"] in plan["members"]],**parameters)
    result.update(configuration_version=plan["configuration_version"],dataset_digest=dataset.digest,
                  market=plan["market"],universe=plan["universe"],biases=plan["biases"])
    return result,ledger

def run_baseline(root:Path,dataset:Dataset,run_dir:Path,*,arms=None):
    plan=read_json(run_dir/"plan.json")
    if not plan: raise ValueError("Freeze a research plan first")
    config=_check(root,dataset,plan)
    arms=arms or config["research"]["arms"]
    if any(a not in config["research"]["arms"] for a in arms): raise ValueError("Unknown entry arm")
    interval=Interval(_interval(plan["folds"][0]["train"]).start,_interval(plan["holdout"]).start)
    guard_training(interval,_interval(plan["holdout"]))
    outputs={}
    for index,arm in enumerate(arms):
        write_json(run_dir/"progress.json",{"stage":"baseline","arm":arm,"completed":index,"total":len(arms),"updated_at":utcnow(),"dataset_kind":dataset.kind})
        result,_=_segment(config,dataset,plan,arm,plan["baseline"],interval)
        result["phase"]="development_baseline"
        write_json(run_dir/"baseline"/(arm+".json"),result)
        outputs[arm]=result["metrics"]
    write_json(run_dir/"baseline-complete.json",{"dataset_digest":dataset.digest,
        "configuration_digest":plan["configuration_digest"],"arms":arms,"completed_at":utcnow()})
    return outputs

def run_walk_forward(root,dataset,run_dir,*,arms=None):
    plan=read_json(run_dir/"plan.json")
    if not plan: raise ValueError("Freeze a research plan first")
    config=_check(root,dataset,plan)
    arms=arms or config["research"]["arms"]
    baseline=read_json(run_dir/"baseline-complete.json")
    if not baseline or baseline["dataset_digest"]!=dataset.digest or baseline["configuration_digest"]!=plan["configuration_digest"] or not set(arms)<=set(baseline["arms"]):
        raise ValueError("Matching baseline must finish before optimization")
    outputs={}
    for arm in arms:
        ledger=_ledger(config,dataset,plan)
        summaries=[]
        equity=[]
        previous=plan["baseline"]
        for i,window in enumerate(plan["folds"]):
            train,test=_interval(window["train"]),_interval(window["test"])
            guard_training(train,_interval(plan["holdout"]))
            guard_training(test,_interval(plan["holdout"]))
            scores=[]
            for j,params in enumerate(candidates(arm)):
                write_json(run_dir/"progress.json",{"stage":"training","arm":arm,"fold":i,
                    "candidate":j+1,"candidates":len(candidates(arm)),"updated_at":utcnow(),"dataset_kind":dataset.kind})
                result,_=_segment(config,dataset,plan,arm,params,train)
                m=result["metrics"]
                scores.append({"scope":"training","parameters":params,"after_tax_return":m["after_tax_return"],
                               "max_drawdown":m["max_drawdown"],"trades":m["closed_trades"]})
            choice=select_candidate(scores,objective=plan["objective"],neighborhood=plan["neighborhood"],
                                    minimum_trades=5,sparse_is_filter=False,max_drawdown=.3)
            frozen={"fold":i,"train":window["train"],"test":window["test"],
                    "selected":choice,"scores":scores,"frozen_at":utcnow(),"dataset_digest":dataset.digest}
            folder=run_dir/"walk_forward"/arm/f"fold-{i:03d}"
            write_json(folder/"selection.json",frozen)
            params=choice["parameters"] if choice else previous
            result,ledger=_segment(config,dataset,plan,arm,params,test,ledger=ledger,allow_entries=choice is not None)
            result["phase"]="ordinary_out_of_sample"
            result["selection"]=choice
            equity.extend(result["equity"])
            write_json(folder/"test.json",result)
            summaries.append({"fold":i,"selected":choice,"metrics":result["metrics"],
                              "end_equity":ledger.equity,"residual_positions":result["residual_positions"]})
            previous=params
        outputs[arm]={"folds":summaries,"after_tax_return":ledger.equity/ledger.initial_capital-1,
                      "metrics":summarize(equity,ledger.initial_capital,ledger.fees,ledger.taxes,ledger.trades,ledger.events),
                      "equity":equity,
                      "capital_model":"Continuous account cash/positions; fixed original sizing capital."}
        write_json(run_dir/"walk_forward"/arm/"summary.json",outputs[arm])
    write_json(run_dir/"walk-forward-complete.json",{"dataset_digest":dataset.digest,
        "configuration_digest":plan["configuration_digest"],"arms":arms,"completed_at":utcnow()})
    write_json(run_dir/"progress.json",{"stage":"development_complete","dataset_kind":dataset.kind,"updated_at":utcnow()})
    return outputs

def freeze_final_selection(root,dataset,run_dir,*,arms=None):
    plan=read_json(run_dir/"plan.json")
    config=_check(root,dataset,plan)
    arms=arms or config["research"]["arms"]
    done=read_json(run_dir/"walk-forward-complete.json")
    if not done or done["dataset_digest"]!=dataset.digest or not set(arms)<=set(done["arms"]):
        raise ValueError("Complete development evaluation before freezing final choices")
    holdout=_interval(plan["holdout"])
    from .research import month_shift
    train=Interval(holdout.start-timedelta(weeks=2) if dataset.frequency=="5m" else month_shift(holdout.start,-6),holdout.start)
    guard_training(train,holdout)
    choices={}
    for arm in arms:
        scores=[]
        for params in candidates(arm):
            result,_=_segment(config,dataset,plan,arm,params,train)
            m=result["metrics"]
            scores.append(dict(scope="training",parameters=params,after_tax_return=m["after_tax_return"],
                               max_drawdown=m["max_drawdown"],trades=m["closed_trades"]))
        choice=select_candidate(scores,objective=plan["objective"],neighborhood=plan["neighborhood"],
                                minimum_trades=5,sparse_is_filter=False,max_drawdown=.3)
        choices[arm]={"selected":choice,"scores":scores}
    frozen={"plan_digest":fingerprint(plan),"dataset_digest":dataset.digest,"choices":choices,
            "training":{"start":train.start.isoformat(),"end":train.end.isoformat()},"frozen_at":utcnow()}
    path=run_dir/"final-selection.json"
    if path.exists(): raise ValueError("Final selection is already frozen")
    write_json(path,frozen)
    return frozen

def consume_holdout(root,plan,run_dir):
    if plan["dataset_kind"]=="yahoo_audited":
        key=fingerprint({k:plan[k] for k in ("market","frequency","universe","members","holdout")})
        registry=root/".private"/"holdout_registry"
        registry.mkdir(parents=True,exist_ok=True,mode=0o700)
        fd=os.open(registry/(key+".json"),os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
        with os.fdopen(fd,"w") as f:
            json.dump({"consumed_at":utcnow(),"plan_digest":fingerprint(plan)},f)
            f.flush();os.fsync(f.fileno())
    descriptor=os.open(run_dir/"holdout-consumed.json",os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    with os.fdopen(descriptor,"w") as f:
        json.dump({"consumed_at":utcnow(),"plan_digest":fingerprint(plan)},f);f.flush();os.fsync(f.fileno())

def run_final_holdout(root,dataset,run_dir):
    plan=read_json(run_dir/"plan.json");config=_check(root,dataset,plan)
    frozen=read_json(run_dir/"final-selection.json")
    if not frozen or frozen["plan_digest"]!=fingerprint(plan) or frozen["dataset_digest"]!=dataset.digest:
        raise ValueError("Matching final selection must be frozen before holdout")
    # Persist consumption before any result is computed. Failed runs also remain consumed.
    consume_holdout(root,plan,run_dir)
    outputs={}
    for arm,choice in frozen["choices"].items():
        baseline,_=_segment(config,dataset,plan,arm,plan["baseline"],_interval(plan["holdout"]))
        selected=choice["selected"]
        optimized,_=_segment(config,dataset,plan,arm,selected["parameters"] if selected else plan["baseline"],
                             _interval(plan["holdout"]),allow_entries=selected is not None)
        baseline["phase"]=optimized["phase"]="final_holdout"
        outputs[arm]={"baseline":baseline,"selected":optimized,"selection":selected}
        write_json(run_dir/"final_holdout"/(arm+".json"),outputs[arm])
    write_json(run_dir/"progress.json",{"stage":"holdout_complete","dataset_kind":dataset.kind,"updated_at":utcnow()})
    return outputs
