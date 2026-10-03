"""Run actual software tests and record their result for the dashboard."""
from pathlib import Path
import sys,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from trendtrade101.storage import read_json,write_json,utcnow

suite=unittest.defaultTestLoader.discover(str(ROOT/"tests"))
result=unittest.TextTestRunner(verbosity=2).run(suite)
state=read_json(ROOT/".private/status.json",read_json(ROOT/"config/project_status.json",{}))
state["verification"]={"tests_passed":result.testsRun-len(result.failures)-len(result.errors)-len(result.skipped),
    "tests_run":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),
    "checked_at":utcnow(),"command":"python3 scripts/check.py","kind":"synthetic_unit_and_pipeline_integration"}
write_json(ROOT/".private/status.json",state)
raise SystemExit(0 if result.wasSuccessful() else 1)
