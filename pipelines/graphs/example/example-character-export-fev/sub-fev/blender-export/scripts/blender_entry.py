"""foreign: experimental Blender 5.1 --background entry for Sub-FEV example-char.blender-export.

Builds the character from character_spec, exports one FBX, re-imports it into an empty scene and writes
blender_result.json (stage log + readback) and character_inventory.json (canonical input for ue-import).
"""

from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path

import bpy
from mathutils import Euler

REQUEST = json.loads(Path(sys.argv[sys.argv.index("--") + 1]).read_text(encoding="utf-8"))
sys.path.insert(0, REQUEST["spec_dir"])
import character_spec as spec  # noqa: E402

OUT = Path(REQUEST["output"])
SCALE_LENGTH = float(REQUEST["scale_length"])  # metres per Blender unit
TO_UNITS = 1.0 / SCALE_LENGTH


def units(v):
    return tuple(c * TO_UNITS for c in v)


def save(name: str, value) -> None:
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=1), encoding="utf-8")


def clear_scene() -> None:
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for collection in (bpy.data.meshes, bpy.data.armatures, bpy.data.actions, bpy.data.materials):
        for block in list(collection):
            collection.remove(block)


def build() -> None:
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = SCALE_LENGTH
    scene.render.fps = spec.ACTION["fps"]
    scene.frame_start, scene.frame_end = spec.ACTION["frames"][0], spec.ACTION["frames"][-1]
    arm_data = bpy.data.armatures.new("Armature")
    arm = bpy.data.objects.new("Armature", arm_data)  # UE drops an FBX node named "Armature"
    scene.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    edit = {}
    for bone in spec.bones():
        eb = arm_data.edit_bones.new(bone["name"])
        eb.head, eb.tail = units(bone["head"]), units(bone["tail"])
        eb.use_deform = bone["half_width"] > 0.0
        if bone["parent"]:
            eb.parent = edit[bone["parent"]]
        edit[bone["name"]] = eb
    bpy.ops.object.mode_set(mode="OBJECT")

    data = spec.mesh()
    me = bpy.data.meshes.new("ExampleCharacter")
    me.from_pydata([units(v) for v in data["vertices"]], [], data["faces"])
    for name in spec.MATERIALS:
        me.materials.append(bpy.data.materials.new(name))
    for poly, index in zip(me.polygons, data["face_materials"]):
        poly.material_index = index
    me.update()
    body = bpy.data.objects.new("ExampleCharacter", me)
    scene.collection.objects.link(body)
    for name, indices in data["groups"].items():
        body.vertex_groups.new(name=name).add(indices, 1.0, "REPLACE")
    body.shape_key_add(name="Basis", from_mix=False)
    for name in spec.SHAPE_KEYS:
        key = body.shape_key_add(name=name, from_mix=False)
        for point, co in zip(key.data, data["shape_keys"][name]):
            point.co = units(co)
    body.parent = arm
    modifier = body.modifiers.new("Armature", "ARMATURE")
    modifier.object = arm

    action = bpy.data.actions.new(spec.ACTION["name"])
    arm.animation_data_create().action = action
    pose_bone = arm.pose.bones[spec.ACTION["bone"]]
    pose_bone.rotation_mode = "XYZ"
    for frame, euler in zip(spec.ACTION["frames"], spec.ACTION["euler_xyz"]):
        pose_bone.rotation_euler = Euler(euler, "XYZ")
        pose_bone.keyframe_insert("rotation_euler", frame=frame)


def readback() -> dict:
    metres = bpy.context.scene.unit_settings.scale_length
    arms = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"]
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    arm = arms[0]
    bones = [{"name": b.name, "parent": b.parent.name if b.parent else None,
              "head_world": [c * metres for c in arm.matrix_world @ b.head_local]} for b in arm.data.bones]
    body = meshes[0]
    keys = body.data.shape_keys.key_blocks if body.data.shape_keys else []
    basis = [v.co.copy() for v in body.data.vertices]
    shape_keys = {}
    for key in keys:
        if key.name == "Basis":
            continue
        shape_keys[key.name] = max((p.co - b).length for p, b in zip(key.data, basis)) * body.matrix_world.to_scale()[0] * metres
    actions = [{"name": a.name, "frame_range": list(a.frame_range)} for a in bpy.data.actions]
    return {"scale_length": metres, "armature_scale": list(arm.matrix_world.to_scale()), "armature_objects": [o.name for o in arms], "mesh_objects": [o.name for o in meshes],
            "armature_matrix_world": [list(r) for r in arm.matrix_world], "bones": bones,
            "vertex_count": len(body.data.vertices), "materials": [m.name for m in body.data.materials if m],
            "shape_key_max_delta_m": shape_keys, "actions": actions}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    result = {"blender": bpy.app.version_string, "stage": "build"}
    try:
        clear_scene()
        build()
        result["source"] = readback()
        result["stage"] = "export"
        fbx = OUT / "character.fbx"
        options = dict(REQUEST["fbx_export"])
        options["object_types"] = set(options["object_types"])
        result["export_status"] = sorted(bpy.ops.export_scene.fbx(filepath=str(fbx), check_existing=False, **options))
        result["stage"] = "reimport"
        clear_scene()
        bpy.ops.import_scene.fbx(filepath=str(fbx), **REQUEST["fbx_import"])
        result["reimport"] = readback()
        save("character_inventory.json", {
            "source": "character_spec via Blender build", "fbx": fbx.name, "scale_length": SCALE_LENGTH, "blender": bpy.app.version_string,
            "bones": result["source"]["bones"], "vertex_count": result["source"]["vertex_count"],
            "materials": result["source"]["materials"], "shape_keys": list(result["source"]["shape_key_max_delta_m"]),
            "action": {"name": spec.ACTION["name"], "fps": spec.ACTION["fps"],
                       "frames": [spec.ACTION["frames"][0], spec.ACTION["frames"][-1]]}})
        result["stage"] = "done"
    except Exception as exc:  # recorded as evidence; host judges the Verdict
        result.update(error_type=type(exc).__name__, error=str(exc), traceback=traceback.format_exc())
    finally:
        save("blender_result.json", result)


main()
