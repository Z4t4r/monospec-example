"""host-evidence: ICD acceptance launcher for OpenSpec change add-example-character-export.

Runs the production code in repos/example-character-tools (unit tests, Blender add-on, headless CLI), imports
the CLI FBX in a fresh isolated AIAGENT UE5.8 Worker and compares everything with the FEV canonical inventory
(data only; no FEV script is imported).

Usage (repository root): python pipelines/graphs/example/example-character-export-acceptance/scripts/run_acceptance.py
Prints RUN=<path>. Exit code 0 only when every check passes.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

GRAPH = Path(__file__).resolve().parents[1]
REPO = GRAPH.parents[3]
GRAPH_ID = "example-character-export-acceptance"
sys.path.insert(0, str(REPO / "pipelines" / "_shared"))
from host_run import file_sha256, finalize_run, load_local_environment, new_run, save_json  # noqa: E402
from host_run import ue_worker  # noqa: E402
from host_run.blender import run_blender  # noqa: E402


def load_yaml(path: Path) -> dict:
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8"))


def check(checks: list, check_id: str, ok: bool, reason: str, evidence: str | None = None) -> bool:
    row = {"id": check_id, "status": "pass" if ok else "fail", "reason": reason}
    if evidence:
        row["evidence"] = evidence
    checks.append(row)
    return ok


def to_ue_cm(v) -> tuple:
    # same mapping as example_character_tools.spec.blender_to_ue_cm; kept local so the check does not trust the code under test
    return (v[0] * 100.0, -v[1] * 100.0, v[2] * 100.0)


def cli(blender: Path, project: Path, args: list, log: Path) -> int:
    command = [str(blender), "--background", "--factory-startup", "--disable-autoexec", "--python-exit-code", "1",
               "--python", str(project / "cli" / "export_character.py"), "--", *args]
    with log.open("w", encoding="utf-8", errors="replace") as handle:
        return subprocess.run(command, stdout=handle, stderr=subprocess.STDOUT, timeout=600).returncode


def inventory_parity(prod: dict, ref: dict, tol_m: float) -> list:
    problems = []
    if [(b["name"], b["parent"]) for b in prod["bones"]] != [(b["name"], b["parent"]) for b in ref["bones"]]:
        problems.append("bone names / parents differ")
    ref_heads = {b["name"]: b["head_world"] for b in ref["bones"]}
    worst = max((max(abs(a - e) for a, e in zip(b["head_world"], ref_heads.get(b["name"], (1e9,) * 3))) for b in prod["bones"]),
                default=float("inf"))
    if worst > tol_m:
        problems.append(f"head error {worst:.3e} m")
    for key in ("vertex_count", "materials"):
        if prod[key] != ref[key]:
            problems.append(f"{key} {prod[key]} != {ref[key]}")
    if sorted(prod["shape_keys"]) != sorted(ref["shape_keys"]):
        problems.append("shape_keys differ")
    length = lambda inv: inv["action"]["frames"][1] - inv["action"]["frames"][0] + 1  # noqa: E731
    if length(prod) != length(ref):
        problems.append("action length differs")
    return problems


def ue_checks(result: dict, inventory: dict, tol: dict, checks: list) -> None:
    classes = result.get("assets_by_class", {})
    check(checks, "L2-ue-assets", all(classes.get(k) for k in ("SkeletalMesh", "Skeleton", "AnimSequence")),
          f"assets_by_class={classes}", "evidence/worker/ue_result.json")
    bones = result.get("bones", [])
    roots = [b["name"] for b in bones if b["parent"] is None]
    same = sorted(((b["name"], b["parent"]) for b in bones), key=str) == \
        sorted(((b["name"], b["parent"]) for b in inventory["bones"]), key=str)
    scaled = [b["name"] for b in bones if max(abs(s - 1.0) for s in b["local_s"]) > tol["scale_abs"]]
    check(checks, "L2-ue-skeleton", bool(bones) and same and roots == ["root"] and not scaled,
          f"{len(bones)} bones, roots {roots}, hierarchy equal {same}, scaled bones {scaled}", "evidence/worker/ue_result.json")
    ue = {b["name"]: b["component_t"] for b in bones}
    errors = {b["name"]: max(abs(a - e) for a, e in zip(ue[b["name"]], to_ue_cm(b["head_world"])))
              for b in inventory["bones"] if b["name"] in ue}
    worst = max(errors.items(), key=lambda kv: kv[1]) if errors else ("none", float("inf"))
    check(checks, "L2-ue-ref-pose", len(errors) == len(inventory["bones"]) and worst[1] <= tol["position_cm"],
          f"worst {worst[0]}: {worst[1]:.4g} cm", "evidence/worker/ue_result.json")
    mesh = result.get("mesh", {})
    length = inventory["action"]["frames"][1] - inventory["action"]["frames"][0] + 1
    frames = [a.get("num_frames") for a in result.get("animations", [])]
    ok = (mesh.get("morph_targets") == sorted(inventory["shape_keys"])
          and len(mesh.get("material_slots", [])) == len(inventory["materials"])
          and any(f in (length, length - 1) for f in frames if isinstance(f, int)))
    check(checks, "L2-ue-morph-material-anim", ok,
          f"morphs {mesh.get('morph_targets')}; slots {mesh.get('material_slots')}; anim frames {frames} / length {length}",
          "evidence/worker/ue_result.json")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args(argv)
    cfg = load_yaml(GRAPH / "config.yaml")
    if cfg["graph"]["status"] != "active":
        raise ValueError("Graph is not active")
    tol = load_yaml(GRAPH / "contract.yaml")["tolerance"]
    project = REPO / cfg["context"]["project"]
    env = load_local_environment()
    started = datetime.now()
    run = new_run(GRAPH)
    evidence = run / "evidence"
    checks: list = []
    reference_path = REPO / cfg["icd"]["fev_canonical_inventory"]
    manifest: dict = {"configuration": {"local_environment": env.describe(), "icd": cfg["icd"]},
                      "input_fingerprint": {
                          "project_files": {p.relative_to(REPO).as_posix(): file_sha256(p)
                                            for p in sorted(project.rglob("*.py")) if "__pycache__" not in p.parts},
                          "fev_canonical_inventory": file_sha256(reference_path) if reference_path.is_file() else "missing"}}

    tests = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"], cwd=project,
                           capture_output=True, text=True, encoding="utf-8")
    (evidence / "unit_tests.log").write_text(tests.stdout + tests.stderr, encoding="utf-8")
    check(checks, "L1-unit-tests", tests.returncode == 0, f"exit_code={tests.returncode}", "evidence/unit_tests.log")

    blender = env.path("blender_executable")
    if blender is None or not blender.is_file():
        check(checks, "L1-cli-exit", False, "blender_executable not configured")
    else:
        request = save_json(evidence / "addon_request.json", {"output": str(evidence / "addon"), "project": str(project)})
        record = run_blender(blender, GRAPH / "scripts" / "blender_addon_check.py", request,
                             log_path=evidence / "addon_blender.log")
        addon_path = evidence / "addon" / "addon_check.json"
        addon = json.loads(addon_path.read_text(encoding="utf-8")) if addon_path.is_file() else {"stage": "missing"}
        manifest.setdefault("environment", {})["blender"] = addon.get("blender")
        check(checks, "L1-addon-register", record["exit_code"] == 0 and addon.get("registered") is True
              and addon.get("unregistered") is True,
              f"exit {record['exit_code']} registered {addon.get('registered')} unregistered {addon.get('unregistered')} "
              f"{addon.get('error', '')}".strip(), "evidence/addon/addon_check.json")

        out = evidence / "cli"
        code = cli(blender, project, ["--output-dir", str(out)], evidence / "cli_blender.log")
        fbx, inv_path = out / "ExampleCharacter.fbx", out / "ExampleCharacter.inventory.json"
        check(checks, "L1-cli-exit", code == 0 and fbx.is_file() and inv_path.is_file(),
              f"exit_code={code}; fbx {fbx.is_file()}; inventory {inv_path.is_file()}", "evidence/cli_blender.log")

        if inv_path.is_file():
            prod = json.loads(inv_path.read_text(encoding="utf-8"))
            if reference_path.is_file() and file_sha256(reference_path) == cfg["icd"]["fev_canonical_sha256"]:
                problems = inventory_parity(prod, json.loads(reference_path.read_text(encoding="utf-8")), tol["position_m"])
                check(checks, "L3-fev-parity", not problems, "; ".join(problems) or "all fields equal",
                      "evidence/cli/ExampleCharacter.inventory.json")
            else:
                check(checks, "L3-fev-parity", False, "FEV canonical inventory missing or sha256 mismatch (rerun FEV first)")
            op_inv = evidence / "addon" / "operator" / "ExampleCharacter.inventory.json"
            op_ok = addon.get("operator_status") == ["FINISHED"] and op_inv.is_file() and \
                not inventory_parity(json.loads(op_inv.read_text(encoding="utf-8")), prod, tol["position_m"])
            check(checks, "L3-operator", op_ok, f"operator_status {addon.get('operator_status')}; inventory equal {op_ok}",
                  "evidence/addon/operator/ExampleCharacter.inventory.json")

        bad = save_json(evidence / "invalid_spec.json", {"bones": [
            {"name": "a", "parent": None, "head": [0, 0, 0], "tail": [0, 0, 1], "half_width": 0.1},
            {"name": "b", "parent": None, "head": [0, 0, 0], "tail": [0, 0, 1], "half_width": 0.1}]})
        bad_out = evidence / "cli_invalid"
        bad_code = cli(blender, project, ["--output-dir", str(bad_out), "--spec", str(bad)], evidence / "cli_invalid.log")
        bad_log = (evidence / "cli_invalid.log").read_text(encoding="utf-8", errors="replace")
        check(checks, "L3-invalid-input", bad_code == 2 and "INVALID_INPUT" in bad_log and not list(bad_out.glob("*.fbx")),
              f"exit_code={bad_code}; INVALID_INPUT {'INVALID_INPUT' in bad_log}; fbx {len(list(bad_out.glob('*.fbx')))}",
              "evidence/cli_invalid.log")

        if fbx.is_file() and inv_path.is_file():
            manifest["outputs"] = {"ExampleCharacter.fbx": file_sha256(fbx)}
            blocked = ue_worker.launch(env=env, run=run, graph_id=GRAPH_ID, owner_id="icd", checks=checks,
                                       manifest=manifest, entry=GRAPH / "scripts" / "ue_readback.py",
                                       request={"destination": cfg["context"]["ue_destination"],
                                                "asset_name": cfg["context"]["ue_asset_name"]},
                                       inputs={"fbx": fbx}, timeout=args.timeout)
            result_path = evidence / "worker" / "ue_result.json"
            if blocked is None and result_path.is_file():
                result = json.loads(result_path.read_text(encoding="utf-8"))
                manifest.setdefault("environment", {})["engine_runtime"] = result.get("engine")
                ue_checks(result, prod, tol, checks)
            else:
                check(checks, "L2-ue-assets", False, f"UE Worker blocked or no readback: {blocked}")

    levels = {}
    for level in ("L1", "L2", "L3"):
        rows = [c for c in checks if c["id"].startswith(level)]
        levels[level] = "PASS" if rows and all(c["status"] == "pass" for c in rows) else "FAIL"
    achieved = "none"
    for level in ("L1", "L2", "L3"):
        if levels[level] != "PASS":
            break
        achieved = level
    icd = {"change": cfg["icd"]["change"], "capability": cfg["icd"]["capability"], "target_level": cfg["icd"]["target_level"],
           "levels": levels, "achieved_level": achieved,
           "note": "L4 not claimed: Blender / UE runtime checks are not in CI"}
    result = finalize_run(run, graph_id=GRAPH_ID, owner_id="icd", graph_dir=GRAPH, started=started,
                          runtime="host CPython + Blender 5.1 --background + UE5.8 AIAGENT Worker", checks=checks,
                          manifest=manifest, icd=icd, extra_sections=[
                              "## ICD", "", f"- target: {icd['target_level']}", f"- levels: {levels}",
                              f"- achieved: **{achieved}**", f"- {icd['note']}", ""])
    return 0 if result == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
