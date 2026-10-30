"""host-transform: experimental launcher for Sub-FEV example-char.ue-import (UE5.8 isolated AIAGENT Worker).

Usage (repository root):
  python pipelines/graphs/example/example-character-export-fev/sub-fev/ue-import/scripts/run_ue_import.py [--source-run <blender-export Run>]
Without --source-run the newest passing blender-export Run is pinned. Prints RUN=<path>.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
import graph  # noqa: E402
import character_spec as spec  # noqa: E402
from host_run import file_sha256, finalize_run, load_local_environment, new_run, save_json  # noqa: E402
from host_run import ue_worker  # noqa: E402

SUB_FEV = "example-char.ue-import"
SUB_DIR = Path(__file__).resolve().parents[1]
SOURCE_SUB_DIR = graph.GRAPH / "sub-fev" / "blender-export"


def compare(result: dict, inventory: dict, contract: dict, checks: list) -> list:
    tol = contract["tolerance"]["position_cm"]
    classes = result.get("assets_by_class", {})
    graph.check(checks, "P1-assets", all(classes.get(k) for k in ("SkeletalMesh", "Skeleton", "AnimSequence")),
                f"assets_by_class={classes}", "evidence/worker/ue_result.json")
    bones = result.get("bones", [])
    got = sorted(((b["name"], b["parent"]) for b in bones), key=str)
    want = sorted(((b["name"], b["parent"]) for b in inventory["bones"]), key=str)
    roots = [b["name"] for b in bones if b["parent"] is None]
    graph.check(checks, "P2-bones", got == want and roots == ["root"],
                f"{len(bones)} UE bones, roots {roots}; extra {sorted(set(got) - set(want), key=str)}; "
                f"missing {sorted(set(want) - set(got), key=str)}", "evidence/worker/ue_result.json")
    ue = {b["name"]: b["component_t"] for b in bones}
    rows = []
    for b in inventory["bones"]:
        expected = spec.blender_to_ue_cm(b["head_world"])
        actual = ue.get(b["name"])
        error = max(abs(a - e) for a, e in zip(actual, expected)) if actual else float("inf")
        rows.append({"bone": b["name"], "expected_cm": expected, "ue_cm": actual, "max_abs_error_cm": error})
    worst = max(rows, key=lambda r: r["max_abs_error_cm"])
    graph.check(checks, "P2-ref-pose", worst["max_abs_error_cm"] <= tol,
                f"worst {worst['bone']}: {worst['max_abs_error_cm']:.4g} cm (tolerance {tol})",
                "evidence/ref_pose_comparison.json")
    scale_tol = contract["tolerance"]["scale_abs"]
    scaled = [(b["name"], [round(s, 6) for s in b["local_s"]]) for b in bones
              if max(abs(s - 1.0) for s in b["local_s"]) > scale_tol]
    graph.check(checks, "P2-bone-scale", bones != [] and not scaled,
                f"bones with local scale != 1: {scaled}", "evidence/worker/ue_result.json")
    mesh = result.get("mesh", {})
    graph.check(checks, "P2-morphs", mesh.get("morph_targets") == sorted(inventory["shape_keys"]),
                f"UE {mesh.get('morph_targets')} / Blender {sorted(inventory['shape_keys'])}", "evidence/worker/ue_result.json")
    graph.check(checks, "P2-materials", len(mesh.get("material_slots", [])) == len(inventory["materials"]),
                f"UE slots {mesh.get('material_slots')} / Blender {inventory['materials']}", "evidence/worker/ue_result.json")
    length = inventory["action"]["frames"][1] - inventory["action"]["frames"][0] + 1
    frames = [a.get("num_frames") for a in result.get("animations", [])]
    graph.check(checks, "P2-animation", any(f in (length, length - 1) for f in frames if isinstance(f, int)),
                f"AnimSequence num_frames {frames}; action length {length} frames", "evidence/worker/ue_result.json")
    return rows


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-run", type=Path, help="blender-export Run directory to pin")
    parser.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args(argv)
    cfg = graph.config()
    contract = graph.contract(SUB_FEV)
    env = load_local_environment()
    started = datetime.now()
    run = new_run(SUB_DIR)
    evidence = run / "evidence"
    checks: list = []
    manifest: dict = {"configuration": {}}
    fev = {"question": contract["question"], "evidence": [], "reproduction":
           "python pipelines/graphs/example/example-character-export-fev/sub-fev/ue-import/scripts/run_ue_import.py "
           "--source-run <blender-export Run>"}

    def finish(verdict: str, outcome: str, interpretation: str, limitations: list, guidance: list, evidence_refs: list) -> int:
        fev.update(verdict=verdict, outcome=outcome, interpretation=interpretation, limitations=limitations,
                   guidance=guidance, evidence=evidence_refs,
                   observations=[f"{c['id']}: {c['status']} - {c['reason']}" for c in checks])
        result = finalize_run(run, graph_id=graph.GRAPH_ID, owner_id=SUB_FEV, graph_dir=graph.GRAPH, started=started,
                              runtime="UE5.8 isolated AIAGENT Worker (-NullRHI)", checks=checks, manifest=manifest, fev=fev)
        return 0 if result == "pass" else 1

    source = args.source_run.resolve() if args.source_run else graph.latest_passing_run(SOURCE_SUB_DIR)
    source_ok = False
    if source is not None and (source / "manifest.json").is_file():
        source_manifest = json.loads((source / "manifest.json").read_text(encoding="utf-8"))
        source_summary = json.loads((source / "summary.json").read_text(encoding="utf-8"))
        fbx = source / "evidence" / "character.fbx"
        pinned = source_manifest.get("outputs", {}).get("character.fbx")
        source_ok = source_summary.get("result") == "pass" and fbx.is_file() and file_sha256(fbx) == pinned
        manifest["input_fingerprint"] = {"source_run": source.relative_to(graph.REPO).as_posix(),
                                         "character.fbx": pinned,
                                         "character_inventory.json": source_manifest["outputs"].get("character_inventory.json")}
    graph.check(checks, "P0-input", source_ok, f"source Run {source.name if source else None}")
    if not source_ok:
        return finish("BLOCKED", "No passing, hash-verified blender-export Run to import.", "The question was not tested.",
                      ["no input"], ["run sub-fev/blender-export first"], [])
    shutil.copy2(source / "evidence" / "character_inventory.json", evidence / "character_inventory.json")
    inventory = json.loads((evidence / "character_inventory.json").read_text(encoding="utf-8"))
    blocked = ue_worker.launch(env=env, run=run, graph_id=graph.GRAPH_ID, owner_id=SUB_FEV,
                               entry=Path(__file__).with_name("ue_entry.py"),
                               request={"destination": cfg["context"]["ue_destination"],
                                        "asset_name": cfg["context"]["ue_asset_name"]},
                               inputs={"fbx": source / "evidence" / "character.fbx"},
                               checks=checks, manifest=manifest, timeout=args.timeout)
    if blocked:
        return finish("BLOCKED", f"UE Worker unavailable: {blocked}", "The question was not tested in UE5.8.",
                      ["Worker launch failed before import"], ["fix the environment and rerun"],
                      ["evidence/launch-error.json"])
    status_path = evidence / "worker" / "status.json"
    status = json.loads(status_path.read_text(encoding="utf-8")) if status_path.is_file() else {"status": "missing"}
    result_path = evidence / "worker" / "ue_result.json"
    result = json.loads(result_path.read_text(encoding="utf-8")) if result_path.is_file() else {}
    manifest.setdefault("environment", {})["engine_runtime"] = result.get("engine")
    if status.get("status") != "ok":
        graph.check(checks, "P1-assets", False, f"Editor entry status {status}", "evidence/worker/status.json")
        return finish("INCONCLUSIVE", "Editor entry did not complete.", "No readback to judge.",
                      ["entry error"], ["inspect evidence/worker/UnrealEditor.log"], ["evidence/worker/status.json"])
    rows = compare(result, inventory, contract, checks)
    save_json(evidence / "ref_pose_comparison.json", rows)
    failed = [c["id"] for c in checks if c["status"] != "pass"]
    verdict = "FEASIBLE" if not failed else ("NOT_FEASIBLE" if "P2-bones" in failed or "P1-assets" in failed
                                             else "PARTIALLY_FEASIBLE")
    return finish(
        verdict,
        "UE5.8 automated import matched every checked property." if not failed else f"Failed checks: {', '.join(failed)}.",
        ("Hypothesis H-axis holds: the Blender FBX can be imported by Editor Python as native assets without manual "
         "fixes." if not failed else "Part of the Blender data changed in UE import; see failed checks and comparison."),
        ["-NullRHI: no rendering or shading checked", "MorphTarget deltas, skin weights and animation curve values "
         "are not compared numerically; names, counts and length only", "one engine build, one procedural character"],
        ["The production exporter can reuse the contract fbx_export settings and the 'Armature' object name",
         "An ICD Graph should re-check bones, ref pose, morphs and animation on the production output"],
        ["evidence/worker/ue_result.json", "evidence/ref_pose_comparison.json", "evidence/worker/UnrealEditor.log",
         "evidence/worker_process.json"])


if __name__ == "__main__":
    sys.exit(main())
