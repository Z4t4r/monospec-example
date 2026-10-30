"""blender-addon (headless entry): Headless CLI: blender --background --factory-startup --python cli/export_character.py -- --output-dir <dir>
[--spec <json>]

Exit codes: 0 exported; 2 invalid input (spec / arguments); 1 export failure. Starts from an empty scene.
``--spec`` accepts a JSON CharacterSpec override (fields of spec.CharacterSpec; bones as lists).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import bpy  # noqa: E402

from example_character_tools.blender_export import export_character  # noqa: E402
from example_character_tools.spec import ActionSpec, BoneSpec, CharacterSpec, default_character  # noqa: E402


def load_spec(path: Path | None) -> CharacterSpec:
    if path is None:
        return default_character()
    raw = json.loads(path.read_text(encoding="utf-8"))
    try:
        bones = tuple(BoneSpec(b["name"], b.get("parent"), tuple(b["head"]), tuple(b["tail"]), float(b["half_width"]))
                      for b in raw["bones"])
        kwargs = {"name": raw.get("name", "ExampleCharacter"), "bones": bones}
        if "action" in raw:
            a = raw["action"]
            kwargs["action"] = ActionSpec(a["name"], a["bone"], int(a["fps"]), tuple(a["frames"]),
                                          tuple(tuple(e) for e in a["euler_xyz"]))
    except (KeyError, TypeError) as exc:
        raise ValueError(f"malformed spec: {exc}") from exc
    spec = CharacterSpec(**kwargs)
    spec.validate()
    return spec


def empty_scene() -> bpy.types.Scene:
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    return bpy.context.scene


def main(argv: list) -> int:
    parser = argparse.ArgumentParser(prog="export_character")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--spec", type=Path)
    args = parser.parse_args(argv)
    try:
        spec = load_spec(args.spec)
    except (ValueError, OSError) as exc:
        print(f"INVALID_INPUT: {exc}", file=sys.stderr)
        return 2
    try:
        record = export_character(spec, args.output_dir, empty_scene())
    except (RuntimeError, OSError) as exc:
        print(f"EXPORT_FAILED: {exc}", file=sys.stderr)
        return 1
    print(f"EXPORTED={args.output_dir / record['fbx']}")
    return 0


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    code = main(argv)
    sys.stdout.flush()
    if code:
        sys.exit(code)
