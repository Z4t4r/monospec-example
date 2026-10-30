"""host-transform: experimental launcher for Sub-FEV example-char.blender-export (Blender 5.1 --background).

Usage (repository root): python pipelines/graphs/example/example-character-export-fev/sub-fev/blender-export/scripts/run_blender_export.py
Prints RUN=<path>. Exit code 0 only when the Run result is pass.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
import graph  # noqa: E402
import character_spec as spec  # noqa: E402
from host_run import file_sha256, finalize_run, load_local_environment, new_run, save_json  # noqa: E402
from host_run.blender import run_blender  # noqa: E402

SUB_FEV = "example-char.blender-export"
SUB_DIR = Path(__file__).resolve().parents[1]


def compare(result: dict, contract: dict, checks: list) -> None:
    tol = contract["tolerance"]
    expected = spec.bones()
    back = result["reimport"]
    names = [(b["name"], b["parent"]) for b in back["bones"]]
    graph.check(checks, "P2-bones", sorted(names, key=str) == sorted(((b["name"], b["parent"]) for b in expected), key=str),
                f"{len(names)} bones re-imported, spec {len(expected)}", "evidence/blender_result.json")
    heads = {b["name"]: b["head_world"] for b in back["bones"]}
    errors = [max(abs(a - e) for a, e in zip(heads.get(b["name"], (1e9,) * 3), b["head"])) for b in expected]
    graph.check(checks, "P2-rest-heads", max(errors) <= tol["position_m"],
                f"max |head - spec| = {max(errors):.3e} m (tolerance {tol['position_m']})", "evidence/blender_result.json")
    data = spec.mesh()
    graph.check(checks, "P2-mesh", back["vertex_count"] == len(data["vertices"]) and back["materials"] == list(spec.MATERIALS),
                f"vertices {back['vertex_count']} / {len(data['vertices'])}; materials {back['materials']}",
                "evidence/blender_result.json")
    want = spec.expected_shape_key_max_delta()
    got = back["shape_key_max_delta_m"]
    delta_err = max(abs(got.get(k, 1e9) - v) for k, v in want.items())
    graph.check(checks, "P2-shape-keys", sorted(got) == sorted(want) and delta_err <= tol["delta_m"],
                f"names {sorted(got)}; max |delta - spec| = {delta_err:.3e} m", "evidence/blender_result.json")
    length = spec.ACTION["frames"][-1] - spec.ACTION["frames"][0] + 1
    armature_actions = [a for a in back["actions"] if a["name"].startswith("Armature")]
    lengths = [round(a["frame_range"][1] - a["frame_range"][0] + 1) for a in armature_actions]
    graph.check(checks, "P2-action", length in lengths,
                f"armature actions {[(a['name'], a['frame_range']) for a in armature_actions]}; length {lengths} / {length}",
                "evidence/blender_result.json")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blender", help="override blender_executable")
    parser.add_argument("--variant", help="unit variant from contract.yaml variants (default: default_variant)")
    parser.add_argument("--timeout", type=int, default=600)
    args = parser.parse_args(argv)
    graph.config()
    contract = graph.contract(SUB_FEV)
    variant = args.variant or contract["default_variant"]
    scale_length = contract["variants"][variant]["scale_length"]
    env = load_local_environment({"blender_executable": args.blender})
    started = datetime.now()
    run = new_run(SUB_DIR)
    evidence = run / "evidence"
    checks: list = []
    manifest: dict = {"configuration": {"variant": variant, "scale_length": scale_length,
                                        "local_environment": env.describe(), "fbx_export": contract["fbx_export"],
                                        "fbx_import": contract["fbx_import"]},
                      "input_fingerprint": {"character_spec.py": file_sha256(graph.GRAPH / "scripts/character_spec.py")}}
    fev = {"question": contract["question"], "evidence": [], "reproduction":
           "python pipelines/graphs/example/example-character-export-fev/sub-fev/blender-export/scripts/run_blender_export.py --variant " + variant}
    blender = env.path("blender_executable")
    if blender is None or not blender.is_file():
        graph.check(checks, "P0-blender-version", False, "blender_executable not configured or missing")
        fev.update(verdict="BLOCKED", outcome="Blender executable unavailable; no experiment ran.", observations=["no Blender run"],
                   interpretation="The question was not tested.", limitations=["environment not configured"],
                   guidance=["configure .local/environment.yaml (see host_run/environment.example.yaml)"])
        finalize_run(run, graph_id=graph.GRAPH_ID, owner_id=SUB_FEV, graph_dir=graph.GRAPH, started=started,
                     runtime="Blender --background", checks=checks, manifest=manifest, fev=fev)
        return 2
    request = save_json(evidence / "request.json", {"output": str(evidence), "spec_dir": str(graph.GRAPH / "scripts"),
                                                    "scale_length": scale_length,
                                                    "fbx_export": contract["fbx_export"], "fbx_import": contract["fbx_import"]})
    record = run_blender(blender, Path(__file__).with_name("blender_entry.py"), request, log_path=evidence / "blender.log",
                         timeout=args.timeout)
    manifest["configuration"]["command"] = record["command"]
    result_path = evidence / "blender_result.json"
    result = json.loads(result_path.read_text(encoding="utf-8")) if result_path.is_file() else {"stage": "missing"}
    manifest.setdefault("environment", {})["blender"] = result.get("blender")
    graph.check(checks, "P0-blender-version", str(result.get("blender", "")).startswith("5.1"),
                f"bpy.app.version_string={result.get('blender')}", "evidence/blender_result.json")
    graph.check(checks, "P0-blender-exit", record["exit_code"] == 0 and result.get("stage") == "done",
                f"exit_code={record['exit_code']} stage={result.get('stage')} {result.get('error', '')}".strip(),
                "evidence/blender.log")
    fbx = evidence / "character.fbx"
    graph.check(checks, "P1-fbx-written", fbx.is_file() and fbx.stat().st_size > 0,
                f"{fbx.stat().st_size if fbx.is_file() else 0} bytes", "evidence/character.fbx")
    if result.get("stage") == "done":
        compare(result, contract, checks)
        manifest["outputs"] = {"character.fbx": file_sha256(fbx),
                               "character_inventory.json": file_sha256(evidence / "character_inventory.json")}
    failed = [c["id"] for c in checks if c["status"] != "pass"]
    p0_failed = [c for c in failed if c.startswith("P0")]
    verdict = "INCONCLUSIVE" if p0_failed else ("FEASIBLE" if not failed else "NOT_FEASIBLE")
    fev.update(
        verdict=verdict,
        outcome=("Blender headless build + FBX export + re-import preserved every checked property."
                 if verdict == "FEASIBLE" else f"Failed checks: {', '.join(failed)}."),
        observations=[f"{c['id']}: {c['status']} - {c['reason']}" for c in checks],
        interpretation=("The default FBX exporter with the contract settings is a usable Blender-side export path for "
                        "this rigid single-root character." if verdict == "FEASIBLE" else
                        "At least one property is lost or changed in the Blender FBX round trip; see failed checks."),
        limitations=["Blender re-import is a Blender-side round trip only; UE behavior is tested by example-char.ue-import",
                     "rigid weights only; no blended weights, no custom normals, no textures"],
        guidance=["Pin evidence/character.fbx and character_inventory.json (sha256 in manifest.json) as ue-import input"],
        evidence=["evidence/blender_result.json", "evidence/character_inventory.json", "evidence/character.fbx",
                  "evidence/blender.log"])
    outcome = finalize_run(run, graph_id=graph.GRAPH_ID, owner_id=SUB_FEV, graph_dir=graph.GRAPH, started=started,
                           runtime="Blender 5.1 --background", checks=checks, manifest=manifest, fev=fev)
    return 0 if outcome == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
