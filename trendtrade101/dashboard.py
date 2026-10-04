"""Expose only generated research summaries and export a standalone UI snapshot."""
from __future__ import annotations
import json
from pathlib import Path
from .storage import read_json,utcnow,write_json

def pilot_progress(root:Path):
    runs=[]
    for folder in sorted((root/".private/pilots").glob("*")):
        plan=read_json(folder/"plan.json")
        if not plan or plan.get("dataset_kind")!="yahoo_daily_pilot":continue
        progress=read_json(folder/"progress.json",{})
        runs.append({"run":folder.name,"market":plan["market"],"interval":plan["interval"],
            "protected_from":plan["protected_from"],"stage":progress.get("stage","pilot_plan_frozen"),
            "baseline_complete":(folder/"baseline-complete.json").exists(),"formal_holdout_consumed":False})
    return runs

def pilot_results(root:Path):
    records=[]
    for folder in sorted((root/".private/pilots").glob("*")):
        plan=read_json(folder/"plan.json")
        if not plan or plan.get("dataset_kind")!="yahoo_daily_pilot":continue
        for path in sorted((folder/"baseline").glob("*.json")):
            r=read_json(path)
            if r.get("dataset_kind")!="yahoo_daily_pilot" or r.get("phase")!="exploratory_daily_pilot":continue
            records.append({"run":folder.name,"market":plan["market"],"frequency":"daily",
                "universe":"existing_25","arm":path.stem,"phase":"exploratory_daily_pilot",
                "metrics":r["metrics"],"equity":[{"time":p["time"],"equity":p["equity"]} for p in r["equity"]],
                "configuration_version":r["configuration_version"],
                "account_initialization":r["account_initialization"],"limitations":r["limitations"],
                "protected_from":plan["protected_from"],"formal_holdout_consumed":False})
    return records

def research_progress(root:Path):
    runs=[]
    for folder in sorted((root/".private/runs").glob("*")):
        plan=read_json(folder/"plan.json")
        if not plan or plan.get("dataset_kind")!="yahoo_audited":continue
        progress=read_json(folder/"progress.json",{})
        runs.append({"run":folder.name,"market":plan["market"],"frequency":plan["frequency"],
                     "universe":plan["universe"],"holdout":plan["holdout"],
                     "stage":progress.get("stage","plan_frozen"),
                     "baseline_complete":(folder/"baseline-complete.json").exists(),
                     "walk_forward_complete":(folder/"walk-forward-complete.json").exists(),
                     "holdout_consumed":(folder/"holdout-consumed.json").exists()})
    return runs

def result_catalog(root:Path):
    records=[]
    base=root/".private"/"runs"
    for folder in sorted(base.glob("*")):
        plan=read_json(folder/"plan.json")
        if not plan or plan.get("dataset_kind")!="yahoo_audited":continue
        progress=read_json(folder/"progress.json",{})
        for armfile in sorted((folder/"baseline").glob("*.json")):
            r=read_json(armfile)
            if r.get("dataset_kind")!="yahoo_audited":continue
            records.append({"run":folder.name,"market":plan["market"],"frequency":plan["frequency"],
                "universe":plan["universe"],"arm":armfile.stem,"phase":r["phase"],
                "metrics":r["metrics"],"equity":[{"time":p["time"],"equity":p["equity"]} for p in r["equity"]],
                "progress":progress.get("stage"),"configuration_version":r["configuration_version"],
                "account_initialization":r.get("account_initialization")})
        for armfolder in sorted((folder/"walk_forward").glob("*")):
            summary=read_json(armfolder/"summary.json")
            if not summary:continue
            records.append({"run":folder.name,"market":plan["market"],"frequency":plan["frequency"],
                "universe":plan["universe"],"arm":armfolder.name,"phase":"ordinary_out_of_sample",
                "metrics":summary["metrics"],"folds":summary["folds"],
                "equity":[{"time":p["time"],"equity":p["equity"]} for p in summary["equity"]],
                "progress":progress.get("stage"),"configuration_version":plan["configuration_version"],
                "account_initialization":"continuous"})
        if progress.get("stage")=="holdout_complete":
            for armfile in sorted((folder/"final_holdout").glob("*.json")):
                pair=read_json(armfile)
                for label in ("baseline","selected"):
                    r=pair[label]
                    records.append({"run":folder.name,"market":plan["market"],"frequency":plan["frequency"],
                        "universe":plan["universe"],"arm":armfile.stem,"phase":"final_holdout_"+label,
                        "metrics":r["metrics"],"equity":[{"time":p["time"],"equity":p["equity"]} for p in r["equity"]],
                        "configuration_version":r["configuration_version"],
                        "account_initialization":r.get("account_initialization")})
    return records+pilot_results(root)

def export_dashboard(root:Path,destination:Path):
    from .readiness import status
    payload=status(root)
    payload["snapshot_mode"]=True
    payload["snapshot_at"]=utcnow()
    web=Path(__file__).parent/"web"
    html=(web/"index.html").read_text()
    html=html.replace('<link rel="stylesheet" href="/style.css">',"<style>"+(web/"style.css").read_text()+"</style>")
    safe=json.dumps(payload,allow_nan=False).replace("<","\\u003c")
    script="<script>window.TRENDTRADE_SNAPSHOT="+safe+";</script><script>"+(web/"app.js").read_text()+"</script>"
    html=html.replace('<script src="/app.js"></script>',script)
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(html)
    return {"file":str(destination),"status":"exported","snapshot_at":payload["snapshot_at"],
            "result_count":len(payload["results"]),"raw_market_data_included":False}
