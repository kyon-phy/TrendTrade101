from __future__ import annotations
import argparse
import json
from pathlib import Path
from .inputs import verify_project_inputs
from .readiness import status, require_ready
from .server import make_server
from .storage import write_json

def main(argv=None):
    parser = argparse.ArgumentParser(description="Auditable research; no live trading")
    parser.add_argument("--root",type=Path,default=Path.cwd())
    commands = parser.add_subparsers(dest="command",required=True)
    commands.add_parser("status")
    commands.add_parser("verify-inputs")
    for command in ("plan","baseline","optimize","freeze-final","holdout"):
        run=commands.add_parser(command)
        run.add_argument("--dataset",type=Path)
        run.add_argument("--run-dir",type=Path,default=Path(".private/runs/current"))
        run.add_argument("--universe",default="existing_25")
        run.add_argument("--synthetic",action="store_true",help="Explicitly use synthetic fixtures, never historical results")
    for command in ("audit-local","audit-pilot-local"):
        audit=commands.add_parser(command)
        audit.add_argument("--capture",required=True,type=Path)
        audit.add_argument("--output",required=True,type=Path)
    for command in ("pilot-plan","pilot-baseline"):
        run=commands.add_parser(command)
        run.add_argument("--dataset",required=True,type=Path)
        run.add_argument("--run-dir",required=True,type=Path)
        run.add_argument("--synthetic",action="store_true",help="Synthetic software test only")
    export=commands.add_parser("export-dashboard")
    export.add_argument("--output",type=Path,required=True)
    dashboard = commands.add_parser("dashboard")
    dashboard.add_argument("--host",default="127.0.0.1")
    dashboard.add_argument("--port",type=int,default=8765)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    if args.command == "dashboard":
        server = make_server(root,args.host,args.port)
        print(f"TrendTrade101 dashboard: http://{args.host}:{server.server_port}",flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
        return 0
    if args.command == "export-dashboard":
        from .dashboard import export_dashboard
        print(json.dumps(export_dashboard(root,args.output)))
        return 0
    if args.command in ("audit-local","audit-pilot-local"):
        from .audit_package import audit_local_charts
        try:
            pilot=args.command=="audit-pilot-local"
            if pilot:
                from .pilot import private_directory
                private_directory(root,args.output)
            print(json.dumps(audit_local_charts(root,args.capture,args.output,pilot=pilot)))
            return 0
        except (ValueError,KeyError,OSError) as exc:
            print(json.dumps({"status":"blocked","error":str(exc)}))
            return 2
    if args.command in ("pilot-plan","pilot-baseline"):
        try:
            from .dataset import load_dataset
            from .pilot import freeze_pilot,run_pilot
            dataset=load_dataset(root,args.dataset,allow_synthetic=args.synthetic,allow_pilot=True)
            if args.synthetic and dataset.kind!="synthetic_pilot_fixture":
                raise ValueError("--synthetic requires a synthetic pilot fixture")
            directory=args.run_dir if args.run_dir.is_absolute() else root/args.run_dir
            action=freeze_pilot if args.command=="pilot-plan" else run_pilot
            result=action(root,dataset,directory)
            print(json.dumps({"status":"synthetic_test_only" if args.synthetic else "completed",
                "phase":args.command,"research_scope":"exploratory_existing25_daily",
                "formal_holdout_consumed":False,"result":result},allow_nan=False))
            return 0
        except (RuntimeError,ValueError,KeyError,OSError,TypeError) as exc:
            print(json.dumps({"status":"blocked","error":str(exc)}))
            return 2
    if args.command in ("plan","baseline","optimize","freeze-final","holdout"):
        try:
            if not args.dataset:
                require_ready(root)
                raise ValueError("Supply --dataset pointing to an audited local dataset.json")
            from .dataset import load_dataset
            from .orchestration import freeze_plan,run_baseline,run_walk_forward,freeze_final_selection,run_final_holdout
            dataset=load_dataset(root,args.dataset,allow_synthetic=args.synthetic)
            directory=args.run_dir if args.run_dir.is_absolute() else root/args.run_dir
            if args.command=="plan": result=freeze_plan(root,dataset,args.universe,directory)
            elif args.command=="baseline": result=run_baseline(root,dataset,directory)
            elif args.command=="optimize": result=run_walk_forward(root,dataset,directory)
            elif args.command=="freeze-final": result=freeze_final_selection(root,dataset,directory)
            else: result=run_final_holdout(root,dataset,directory)
            print(json.dumps({"status":"synthetic_test_only" if args.synthetic else "completed",
                              "phase":args.command,"run_directory":str(directory),"result":result},allow_nan=False))
            return 0
        except (RuntimeError,ValueError,KeyError,OSError,TypeError) as exc:
            print(json.dumps({"status":"blocked","error":str(exc)}))
            return 2
    report = verify_project_inputs(root) if args.command=="verify-inputs" else status(root)
    if args.command=="verify-inputs":
        write_json(root/".private/input_verification.json",report)
    print(json.dumps(report,indent=2,allow_nan=False))
    return 2 if args.command=="verify-inputs" and report["status"]!="verified" else 0

if __name__ == "__main__":
    raise SystemExit(main())
