from __future__ import annotations
import argparse
import json
from pathlib import Path
from .inputs import verify, input_directory
from .readiness import status, require_ready
from .server import make_server
from .storage import write_json

def main(argv=None):
    parser = argparse.ArgumentParser(description="Auditable research; no live trading")
    parser.add_argument("--root",type=Path,default=Path.cwd())
    commands = parser.add_subparsers(dest="command",required=True)
    commands.add_parser("status")
    commands.add_parser("verify-inputs")
    commands.add_parser("baseline",help="Check real-data baseline prerequisites")
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
    if args.command == "baseline":
        try:
            require_ready(root)
        except RuntimeError as exc:
            print(json.dumps({"status":"blocked","error":str(exc)}))
            return 2
        # Removal of this guard requires the audited orchestration integration.
        print(json.dumps({"status":"blocked","error":"Real-data orchestration is not enabled"}))
        return 2
    report = verify(input_directory(root)) if args.command=="verify-inputs" else status(root)
    if args.command=="verify-inputs":
        write_json(root/".private/input_verification.json",report)
    print(json.dumps(report,indent=2,allow_nan=False))
    return 2 if args.command=="verify-inputs" and report["status"]!="verified" else 0

if __name__ == "__main__":
    raise SystemExit(main())
