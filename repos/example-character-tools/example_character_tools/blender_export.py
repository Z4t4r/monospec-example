"""Blender 5.1 build and FBX export of a CharacterSpec (requires bpy).

The unit rule comes from Root FEV example-char: scene ``scale_length`` 0.01 with data in centimetres, so the
FBX unit factor is 1 and UE does not write a scale of 100 into the root bone.
"""

from __future__ import annotations

import json
from pathlib import Path

import bpy
from mathutils import Euler

from .spec import CharacterSpec, mesh_data

SCALE_LENGTH = 0.01  # metres per Blender unit
ARMATURE_NAME = "Armature"  # UE drops an FBX node with this name, so "root" stays the single root bone

FBX_EXPORT_SETTINGS = {
    "object_types": {"ARMATURE", "MESH"}, "use_selection": False, "apply_unit_scale": True,
    "apply_scale_options": "FBX_SCALE_NONE", "global_scale": 1.0, "axis_forward": "-Z", "axis_up": "Y",
    "use_mesh_modifiers": True, "mesh_smooth_type": "FACE", "add_leaf_bones": False,
    "primary_bone_axis": "Y", "secondary_bone_axis": "X", "use_armature_deform_only": False,
    "armature_nodetype": "NULL", "bake_anim": True, "bake_anim_use_all_bones": True,
    "bake_anim_use_nla_strips": False, "bake_anim_use_all_actions": False,
    "bake_anim_force_startend_keying": True, "bake_anim_simplify_factor": 0.0, "path_mode": "STRIP",
}


def _units(v):
    return tuple(c / SCALE_LENGTH for c in v)


def build_character(spec: CharacterSpec, scene: bpy.types.Scene) -> bpy.types.Object:
    """Create armature, mesh, shape keys, materials and action in ``scene``; return the armature object."""
    data = mesh_data(spec)  # validates the spec before touching the scene
    if any(o.name in (ARMATURE_NAME, spec.name) for o in scene.objects):
        raise ValueError(f"scene already contains {ARMATURE_NAME!r} or {spec.name!r}")
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = SCALE_LENGTH
    scene.render.fps = spec.action.fps
    scene.frame_start, scene.frame_end = spec.action.frames[0], spec.action.frames[-1]

    arm_data = bpy.data.armatures.new(ARMATURE_NAME)
    arm = bpy.data.objects.new(ARMATURE_NAME, arm_data)
    scene.collection.objects.link(arm)
    view_layer = bpy.context.view_layer
    previous_active = view_layer.objects.active
    view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")  # edit bones have no Data API outside Edit Mode
    try:
        edit = {}
        for bone in spec.bones:
            eb = arm_data.edit_bones.new(bone.name)
            eb.head, eb.tail = _units(bone.head), _units(bone.tail)
            eb.use_deform = bone.half_width > 0.0
            if bone.parent is not None:
                eb.parent = edit[bone.parent]
            edit[bone.name] = eb
    finally:
        bpy.ops.object.mode_set(mode="OBJECT")
        if previous_active is not None:
            view_layer.objects.active = previous_active

    me = bpy.data.meshes.new(spec.name)
    me.from_pydata([_units(v) for v in data.vertices], [], data.faces)
    for name in spec.materials:
        me.materials.append(bpy.data.materials.get(name) or bpy.data.materials.new(name))
    for poly, index in zip(me.polygons, data.face_materials):
        poly.material_index = index
    me.update()
    body = bpy.data.objects.new(spec.name, me)
    scene.collection.objects.link(body)
    for name, indices in data.groups.items():
        body.vertex_groups.new(name=name).add(indices, 1.0, "REPLACE")
    body.shape_key_add(name="Basis", from_mix=False)
    for name in spec.shape_keys:
        key = body.shape_key_add(name=name, from_mix=False)
        for point, co in zip(key.data, data.shape_keys[name]):
            point.co = _units(co)
    body.parent = arm
    body.modifiers.new("Armature", "ARMATURE").object = arm

    action = bpy.data.actions.new(spec.action.name)
    arm.animation_data_create().action = action
    pose_bone = arm.pose.bones[spec.action.bone]
    pose_bone.rotation_mode = "XYZ"
    for frame, euler in zip(spec.action.frames, spec.action.euler_xyz):
        pose_bone.rotation_euler = Euler(euler, "XYZ")
        pose_bone.keyframe_insert("rotation_euler", frame=frame)
    return arm


def inventory(spec: CharacterSpec, arm: bpy.types.Object) -> dict:
    """Readback in metres: the comparison record consumed by acceptance Graphs."""
    metres = bpy.context.scene.unit_settings.scale_length
    body = next(o for o in arm.children if o.type == "MESH")
    return {"name": spec.name, "scale_length": metres,
            "bones": [{"name": b.name, "parent": b.parent.name if b.parent else None,
                       "head_world": [c * metres for c in arm.matrix_world @ b.head_local]} for b in arm.data.bones],
            "vertex_count": len(body.data.vertices), "materials": [m.name for m in body.data.materials if m],
            "shape_keys": [k.name for k in body.data.shape_keys.key_blocks if k.name != "Basis"],
            "action": {"name": spec.action.name, "fps": spec.action.fps,
                       "frames": [spec.action.frames[0], spec.action.frames[-1]]}}


def export_fbx(path: Path) -> None:
    """Export the whole scene with FBX_EXPORT_SETTINGS; raise RuntimeError when the operator does not finish."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    status = bpy.ops.export_scene.fbx(filepath=str(path), check_existing=False, **FBX_EXPORT_SETTINGS)
    if "FINISHED" not in status or not path.is_file():
        raise RuntimeError(f"FBX export did not finish: {sorted(status)}")


def export_character(spec: CharacterSpec, output_dir: Path, scene: bpy.types.Scene | None = None) -> dict:
    """Build ``spec`` into ``scene`` (default: current scene), export ``<name>.fbx`` and ``<name>.inventory.json``."""
    scene = scene or bpy.context.scene
    arm = build_character(spec, scene)
    output_dir = Path(output_dir)
    fbx = output_dir / f"{spec.name}.fbx"
    export_fbx(fbx)
    record = inventory(spec, arm)
    record["fbx"] = fbx.name
    (output_dir / f"{spec.name}.inventory.json").write_text(json.dumps(record, indent=1), encoding="utf-8")
    return record
