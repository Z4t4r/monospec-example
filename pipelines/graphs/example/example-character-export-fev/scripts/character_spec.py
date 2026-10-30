"""host-transform: experimental procedural character used as the FEV input (no external asset).

Pure Python and deterministic, so the Blender entry and the host comparison share one definition.
Units: metres, Blender Z-up, the character faces -Y. Every deform bone owns one axis-aligned box
rigidly weighted to it. Not a business API; production code lives in repos/example-character-tools.
"""

from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

Vec = Tuple[float, float, float]

_CENTER_BONES: Sequence[Tuple[str, str | None, Vec, Vec, float]] = (
    ("root", None, (0.0, 0.0, 0.0), (0.0, 0.0, 0.15), 0.0),
    ("pelvis", "root", (0.0, 0.0, 0.95), (0.0, 0.0, 1.10), 0.14),
    ("spine_01", "pelvis", (0.0, 0.0, 1.10), (0.0, 0.0, 1.30), 0.13),
    ("spine_02", "spine_01", (0.0, 0.0, 1.30), (0.0, 0.0, 1.50), 0.15),
    ("neck_01", "spine_02", (0.0, 0.0, 1.50), (0.0, 0.0, 1.62), 0.05),
    ("head", "neck_01", (0.0, 0.0, 1.62), (0.0, 0.0, 1.90), 0.11),
)
_LEFT_BONES: Sequence[Tuple[str, str, Vec, Vec, float]] = (
    ("upperarm_l", "spine_02", (0.20, 0.0, 1.45), (0.48, 0.0, 1.45), 0.05),
    ("lowerarm_l", "upperarm_l", (0.48, 0.0, 1.45), (0.74, 0.0, 1.45), 0.04),
    ("hand_l", "lowerarm_l", (0.74, 0.0, 1.45), (0.86, 0.0, 1.45), 0.035),
    ("thigh_l", "pelvis", (0.11, 0.0, 0.95), (0.11, 0.0, 0.52), 0.07),
    ("calf_l", "thigh_l", (0.11, 0.0, 0.52), (0.11, 0.0, 0.10), 0.055),
    ("foot_l", "calf_l", (0.11, 0.0, 0.10), (0.11, -0.14, 0.02), 0.045),
)

MATERIALS = ("M_Body", "M_Head")
SHAPE_KEYS = ("head_scale_up", "belly_out")
ACTION = {"name": "wave", "bone": "upperarm_l", "fps": 30, "frames": (1, 15, 30),
          "euler_xyz": ((0.0, 0.0, 0.0), (0.0, -1.2, 0.0), (0.0, 0.0, 0.0))}


def _mirror(name: str) -> str:
    return name[:-2] + "_r" if name.endswith("_l") else name


def bones() -> List[dict]:
    rows = [{"name": n, "parent": p, "head": h, "tail": t, "half_width": w} for n, p, h, t, w in _CENTER_BONES]
    for n, p, h, t, w in _LEFT_BONES:
        rows.append({"name": n, "parent": p, "head": h, "tail": t, "half_width": w})
    for n, p, h, t, w in _LEFT_BONES:
        rows.append({"name": _mirror(n), "parent": _mirror(p), "head": (-h[0], h[1], h[2]),
                     "tail": (-t[0], t[1], t[2]), "half_width": w})
    return rows


def _box(head: Vec, tail: Vec, w: float) -> List[Vec]:
    lo = [min(head[i], tail[i]) - w for i in range(3)]
    hi = [max(head[i], tail[i]) + w for i in range(3)]
    return [(x, y, z) for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]


# vertex order of _box: index = 4*ix + 2*iy + iz; faces wound outward
_BOX_FACES = ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3))


def mesh() -> dict:
    """Vertices, quad faces, per-face material index, rigid vertex groups and shape key positions."""
    vertices: List[Vec] = []
    faces: List[Tuple[int, int, int, int]] = []
    face_materials: List[int] = []
    groups: Dict[str, List[int]] = {}
    for bone in bones():
        if bone["half_width"] <= 0.0:
            continue
        base = len(vertices)
        vertices.extend(_box(bone["head"], bone["tail"], bone["half_width"]))
        faces.extend(tuple(base + i for i in face) for face in _BOX_FACES)
        face_materials.extend([1 if bone["name"] == "head" else 0] * len(_BOX_FACES))
        groups[bone["name"]] = list(range(base, base + 8))
    shape_keys = {name: list(vertices) for name in SHAPE_KEYS}
    head = groups["head"]
    center = tuple(sum(vertices[i][k] for i in head) / len(head) for k in range(3))
    for i in head:
        shape_keys["head_scale_up"][i] = tuple(center[k] + 1.25 * (vertices[i][k] - center[k]) for k in range(3))
    belly = groups["spine_01"]
    front = min(vertices[i][1] for i in belly)
    for i in belly:
        x, y, z = vertices[i]
        if y == front:
            shape_keys["belly_out"][i] = (x, y - 0.05, z)
    return {"vertices": vertices, "faces": faces, "face_materials": face_materials, "groups": groups,
            "shape_keys": shape_keys}


def expected_shape_key_max_delta() -> Dict[str, float]:
    data = mesh()
    result = {}
    for name, positions in data["shape_keys"].items():
        result[name] = max(sum((a - b) ** 2 for a, b in zip(p, v)) ** 0.5
                           for p, v in zip(positions, data["vertices"]))
    return result


def blender_to_ue_cm(v: Sequence[float]) -> Vec:
    """Hypothesis H-axis: FBX export -Z forward / Y up + UE convert_scene maps (x, y, z) m -> (x, -y, z) cm."""
    return (v[0] * 100.0, -v[1] * 100.0, v[2] * 100.0)
