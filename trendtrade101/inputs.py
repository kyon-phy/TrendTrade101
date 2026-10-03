"""Validate exact supplied files; never reconstruct or reselect a universe."""
from __future__ import annotations
import csv
import json
from pathlib import Path
from .storage import sha256, utcnow

EXPECTED = {
    "TrendTrade101_Backtest_Configuration.md": "707cf2472d97d535061395a439fbe81764e9fec53b303edb88419d90c5553bce",
    "frozen_universe_members.csv": "6441e090ca88ad8dd5d557b3cdbcca3d71971bec0c0070a750f67ca069a8e2b0",
    "frozen_universe_manifest.json": "3ee4c294809fe90619fe9eb06dbb110b53c6526ae21c47396a86f9a54a304b07",
    "frozen_universe_manifest.md": "7c4cee332c1e5b5d04f7e938c40bf30661cceb996fb997551a700e000e220af7",
}
PUBLIC_EXPECTED = {
    "TrendTrade101_Backtest_Configuration.md": "ea3038c311c00be7db448ee63ac7454c59f5ad91e88a38068c47ddad945a30b7",
    "frozen_universe_members.csv": "c8908f73ea09ffa39a8aca1c486e87fc9c92635ed246ccc7a019842cf180f0f7",
    "frozen_universe_manifest.json": "72dc94bc16ae38fef13213ab59751d6dfb877cee20cca8ac00d39526dc89b7e5",
    "frozen_universe_manifest.md": "04378fcb29c0944e784edda5a0f86b6c177be4222f7a8ce50bafdbcc49e82e95",
    "public_input_provenance.json": "18a38bbaa2817e1b295dd0c1cd0086ad66070c4a32d864a23eb73b0a4ecdcf38",
}

class InputError(ValueError):
    pass

def input_directory(root: Path) -> Path:
    """Prefer an explicit reviewed public input directory when present."""
    public = root / "config" / "inputs"
    return public if public.is_dir() else root / ".private" / "inputs"

def verify(directory: Path, *, kind: str = "original_source") -> dict:
    if kind not in ("original_source", "public_derived"):
        raise InputError("Unknown input verification route")
    expected_files = EXPECTED if kind == "original_source" else PUBLIC_EXPECTED
    checks, problems = [], []
    for name, expected in expected_files.items():
        p = directory / name
        actual = sha256(p) if p.is_file() else None
        ok = actual == expected
        checks.append({"name": name, "expected_sha256": expected, "actual_sha256": actual, "verified": ok})
        if not ok:
            problems.append(f"{name}: " + ("missing" if actual is None else "hash mismatch"))
    report = {"checked_at": utcnow(), "status": "blocked" if problems else "verified",
              "verification_kind":kind, "original_bytes_verified":False,
              "files": checks, "problems": problems, "membership_count": None, "unique_securities": None}
    if problems:
        return report
    if kind == "public_derived":
        provenance = json.loads((directory / "public_input_provenance.json").read_text())
        if provenance["publication_kind"] != "sanitized_public_projection":
            raise InputError("Wrong public provenance type")
        if provenance["source_configuration_version"] != "v0.13" or not (
            provenance["strategy_parameters_unchanged"] and provenance["membership_and_order_unchanged"]):
            raise InputError("Unapproved public derivation")
        for item in provenance["files"]:
            if item["source_sha256"] != EXPECTED[item["name"]] or item["public_sha256"] != PUBLIC_EXPECTED[item["name"]]:
                raise InputError("Source/public provenance hash mismatch")
            if (directory/item["name"]).stat().st_size != item["public_size_bytes"]:
                raise InputError("Public input byte count mismatch")
        report["provenance"] = {
            "publication_kind":provenance["publication_kind"],
            "source_configuration_version":provenance["source_configuration_version"],
            "strategy_parameters_unchanged":True, "membership_and_order_unchanged":True,
            "description":"Authorized sanitized public derivatives. Original Library bytes were not verified in this executor."}
    else:
        report["original_bytes_verified"] = True
    with (directory / "frozen_universe_members.csv").open(newline="",encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    manifest = json.loads((directory / "frozen_universe_manifest.json").read_text())
    csv_metadata = next(f for f in manifest["files"] if f["name"] == "frozen_universe_members.csv")
    if csv_metadata["sha256"] != expected_files["frozen_universe_members.csv"]:
        raise InputError("Manifest CSV checksum does not match selected route")
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

def verify_project_inputs(root: Path) -> dict:
    directory = input_directory(root)
    kind = "public_derived" if directory == root/"config"/"inputs" else "original_source"
    return verify(directory,kind=kind)

def require_verified(directory: Path, *, kind: str = "original_source") -> list[dict]:
    report = verify(directory,kind=kind)
    if report["status"] != "verified":
        raise InputError("; ".join(report["problems"]))
    with (directory / "frozen_universe_members.csv").open(newline="",encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def project_members(root: Path) -> list[dict]:
    directory = input_directory(root)
    return require_verified(directory,kind="public_derived" if directory == root/"config"/"inputs" else "original_source")

def symbols_for(rows: list[dict], market: str, universe: str, frequency: str) -> list[str]:
    return [r["ticker"] for r in rows if r["market"] == market and r["universe_id"] == universe
            and r["frequency"] in (frequency, "daily_and_5m")]
