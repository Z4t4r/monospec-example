"""foreign: experimental UE5.8 Editor Python entry for Sub-FEV example-char.ue-import.

Runs inside a fresh AIAGENT Worker project. Imports the pinned FBX as SkeletalMesh + Skeleton + AnimSequence,
saves only inside the Worker, then reads back bones, reference pose, MorphTargets, material slots and animation.
"""
from __future__ import annotations

import json
import os
import traceback
from collections import Counter
from pathlib import Path

import unreal as u

REQUEST = json.loads(Path(os.environ["MONOSPEC_WORKER_REQUEST"]).read_text(encoding="utf-8"))
OUT = Path(REQUEST["output"])


def save(name: str, value) -> None:
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=1), encoding="utf-8")


def attempt(fn):
    try:
        return fn()
    except Exception as exc:  # UE reflection raises generic Exception; record and continue
        return {"unavailable": f"{type(exc).__name__}: {exc}"}


def vec(v) -> list:
    return [float(v.x), float(v.y), float(v.z)]


def import_fbx() -> list:
    task = u.AssetImportTask()
    task.set_editor_property("filename", REQUEST["fbx"])
    task.set_editor_property("destination_path", REQUEST["destination"])
    task.set_editor_property("destination_name", REQUEST["asset_name"])
    task.set_editor_property("automated", True)
    task.set_editor_property("replace_existing", True)
    task.set_editor_property("save", True)
    options = u.FbxImportUI()
    options.set_editor_property("import_mesh", True)
    options.set_editor_property("import_as_skeletal", True)
    options.set_editor_property("mesh_type_to_import", u.FBXImportType.FBXIT_SKELETAL_MESH)
    options.set_editor_property("import_materials", True)
    options.set_editor_property("import_textures", False)
    options.set_editor_property("import_animations", True)
    options.set_editor_property("create_physics_asset", False)
    data = options.get_editor_property("skeletal_mesh_import_data")
    data.set_editor_property("import_morph_targets", True)
    data.set_editor_property("convert_scene", True)
    data.set_editor_property("convert_scene_unit", True)
    data.set_editor_property("use_t0_as_ref_pose", False)
    options.set_editor_property("skeletal_mesh_import_data", data)
    task.set_editor_property("options", options)
    u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    return [str(p) for p in task.get_editor_property("imported_object_paths")]


def skeleton_readback(mesh) -> list:
    modifier = u.SkeletonModifier()
    modifier.set_skeletal_mesh(mesh)
    bones = []
    for name in modifier.get_all_bone_names():
        b = str(name)
        parent = str(modifier.get_parent_name(b))
        local = modifier.get_bone_transform(b, False)
        bones.append({"name": b, "parent": None if parent in ("None", "") else parent,
                      "component_t": vec(modifier.get_bone_transform(b, True).translation),
                      "local_t": vec(local.translation), "local_s": vec(local.scale3d)})
    return bones


def anim_readback(anim) -> dict:
    lib = u.AnimationLibrary
    return {"asset": anim.get_path_name(),
            "num_frames": attempt(lambda: lib.get_num_frames(anim)),
            "num_keys": attempt(lambda: lib.get_num_keys(anim)),
            "play_length_s": attempt(lambda: float(anim.get_play_length())),
            "track_names": attempt(lambda: sorted(str(n) for n in lib.get_animation_track_names(anim))),
            "skeleton": attempt(lambda: anim.get_editor_property("skeleton").get_path_name())}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    result: dict = {"engine": u.SystemLibrary.get_engine_version(), "destination": REQUEST["destination"]}
    try:
        result["imported_object_paths"] = import_fbx()
        u.EditorAssetLibrary.save_directory(REQUEST["destination"], only_if_is_dirty=False, recursive=True)
        registry = u.AssetRegistryHelpers.get_asset_registry()
        registry.scan_paths_synchronous([REQUEST["destination"]], True)
        assets = registry.get_assets_by_path(REQUEST["destination"], recursive=True)
        result["assets"] = sorted(f"{a.asset_class_path.asset_name}:{a.package_name}" for a in assets)
        result["assets_by_class"] = dict(Counter(str(a.asset_class_path.asset_name) for a in assets))
        mesh = u.load_asset(f"{REQUEST['destination']}/{REQUEST['asset_name']}")
        if isinstance(mesh, u.SkeletalMesh):
            sub = u.get_editor_subsystem(u.SkeletalMeshEditorSubsystem)
            result["mesh"] = {
                "asset": mesh.get_path_name(),
                "skeleton": mesh.get_editor_property("skeleton").get_path_name(),
                "morph_targets": attempt(lambda: sorted(t.get_name() for t in mesh.get_editor_property("morph_targets"))),
                "material_slots": [str(s.get_editor_property("material_slot_name")) for s in mesh.get_editor_property("materials")],
                "lod0_vertices": attempt(lambda: sub.get_num_verts(mesh, 0)),
                "bounds_extent": vec(mesh.get_bounds().box_extent)}
            result["bones"] = skeleton_readback(mesh)
        anims = [u.load_asset(str(a.package_name)) for a in assets if str(a.asset_class_path.asset_name) == "AnimSequence"]
        result["animations"] = [anim_readback(a) for a in anims if a is not None]
        save("ue_result.json", result)
        save("status.json", {"status": "ok"})
    except Exception as exc:  # recorded as evidence; host judges the Verdict
        save("ue_result.json", result)
        save("status.json", {"status": "error", "error_type": type(exc).__name__, "error": str(exc),
                             "traceback": traceback.format_exc()})
    finally:
        u.SystemLibrary.quit_editor()


main()
