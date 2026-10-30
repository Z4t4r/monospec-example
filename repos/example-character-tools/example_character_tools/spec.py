"""Character description for the example exporter; pure Python, no bpy (unit-testable on host CPython).

Units: metres, Blender Z-up, the character faces -Y. Every deform bone owns one axis-aligned box rigidly
weighted to it. Behavior follows Root FEV example-char (pipelines/graphs/example/example-character-export-fev).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Tuple

Vec = Tuple[float, float, float]


@dataclass(frozen=True)
class BoneSpec:
    name: str
    parent: str | None
    head: Vec
    tail: Vec
    half_width: float  # 0 -> non-deform bone without geometry


@dataclass(frozen=True)
class ActionSpec:
    name: str
    bone: str
    fps: int
    frames: Tuple[int, ...]
    euler_xyz: Tuple[Vec, ...]

    @property
    def length(self) -> int:
        return self.frames[-1] - self.frames[0] + 1


@dataclass(frozen=True)
class CharacterSpec:
    name: str
    bones: Tuple[BoneSpec, ...]
    materials: Tuple[str, ...] = ("M_Body", "M_Head")
    head_bone: str = "head"
    shape_keys: Tuple[str, ...] = ("head_scale_up", "belly_out")
    action: ActionSpec = field(default_factory=lambda: ActionSpec(
        "wave", "upperarm_l", 30, (1, 15, 30), ((0.0, 0.0, 0.0), (0.0, -1.2, 0.0), (0.0, 0.0, 0.0))))

    def validate(self) -> None:
        """Raise ValueError for a spec that cannot become a single-root UE skeleton."""
        names = [b.name for b in self.bones]
        if len(set(names)) != len(names):
            raise ValueError("bone names must be unique")
        if not all(n and n.isascii() and " " not in n for n in names):
            raise ValueError("bone names must be non-empty ASCII without spaces")
        roots = [b.name for b in self.bones if b.parent is None]
        if len(roots) != 1:
            raise ValueError(f"exactly one root bone required, got {roots}")
        seen = set()
        for bone in self.bones:
            if bone.parent is not None and bone.parent not in seen:
                raise ValueError(f"parent {bone.parent!r} of {bone.name!r} must be declared before it")
            if bone.half_width < 0.0:
                raise ValueError(f"half_width of {bone.name!r} must be >= 0")
            seen.add(bone.name)
        if self.action.bone not in seen:
            raise ValueError(f"action bone {self.action.bone!r} is not a bone")
        if len(self.action.frames) != len(self.action.euler_xyz) or list(self.action.frames) != sorted(self.action.frames):
            raise ValueError("action frames must be sorted and match euler_xyz")


_CENTER = (
    ("root", None, (0.0, 0.0, 0.0), (0.0, 0.0, 0.15), 0.0),
    ("pelvis", "root", (0.0, 0.0, 0.95), (0.0, 0.0, 1.10), 0.14),
    ("spine_01", "pelvis", (0.0, 0.0, 1.10), (0.0, 0.0, 1.30), 0.13),
    ("spine_02", "spine_01", (0.0, 0.0, 1.30), (0.0, 0.0, 1.50), 0.15),
    ("neck_01", "spine_02", (0.0, 0.0, 1.50), (0.0, 0.0, 1.62), 0.05),
    ("head", "neck_01", (0.0, 0.0, 1.62), (0.0, 0.0, 1.90), 0.11),
)
_LEFT = (
    ("upperarm_l", "spine_02", (0.20, 0.0, 1.45), (0.48, 0.0, 1.45), 0.05),
    ("lowerarm_l", "upperarm_l", (0.48, 0.0, 1.45), (0.74, 0.0, 1.45), 0.04),
    ("hand_l", "lowerarm_l", (0.74, 0.0, 1.45), (0.86, 0.0, 1.45), 0.035),
    ("thigh_l", "pelvis", (0.11, 0.0, 0.95), (0.11, 0.0, 0.52), 0.07),
    ("calf_l", "thigh_l", (0.11, 0.0, 0.52), (0.11, 0.0, 0.10), 0.055),
    ("foot_l", "calf_l", (0.11, 0.0, 0.10), (0.11, -0.14, 0.02), 0.045),
)


def _mirror(name: str) -> str:
    return name[:-2] + "_r" if name.endswith("_l") else name


def default_character() -> CharacterSpec:
    bones = [BoneSpec(*row) for row in _CENTER]
    bones += [BoneSpec(*row) for row in _LEFT]
    bones += [BoneSpec(_mirror(n), _mirror(p), (-h[0], h[1], h[2]), (-t[0], t[1], t[2]), w) for n, p, h, t, w in _LEFT]
    return CharacterSpec(name="ExampleCharacter", bones=tuple(bones))


def _box(head: Vec, tail: Vec, w: float) -> List[Vec]:
    lo = [min(head[i], tail[i]) - w for i in range(3)]
    hi = [max(head[i], tail[i]) + w for i in range(3)]
    return [(x, y, z) for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]


BOX_FACES = ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3))


@dataclass(frozen=True)
class MeshData:
    vertices: List[Vec]
    faces: List[Tuple[int, int, int, int]]
    face_materials: List[int]
    groups: Dict[str, List[int]]
    shape_keys: Dict[str, List[Vec]]


def mesh_data(spec: CharacterSpec) -> MeshData:
    spec.validate()
    vertices: List[Vec] = []
    faces: List[Tuple[int, int, int, int]] = []
    face_materials: List[int] = []
    groups: Dict[str, List[int]] = {}
    for bone in spec.bones:
        if bone.half_width == 0.0:
            continue
        base = len(vertices)
        vertices.extend(_box(bone.head, bone.tail, bone.half_width))
        faces.extend(tuple(base + i for i in face) for face in BOX_FACES)
        face_materials.extend([1 if bone.name == spec.head_bone else 0] * len(BOX_FACES))
        groups[bone.name] = list(range(base, base + 8))
    keys: Dict[str, List[Vec]] = {name: list(vertices) for name in spec.shape_keys}
    if "head_scale_up" in keys:
        head = groups[spec.head_bone]
        center = tuple(sum(vertices[i][k] for i in head) / len(head) for k in range(3))
        for i in head:
            keys["head_scale_up"][i] = tuple(center[k] + 1.25 * (vertices[i][k] - center[k]) for k in range(3))
    if "belly_out" in keys:
        belly = groups["spine_01"]
        front = min(vertices[i][1] for i in belly)
        for i in belly:
            x, y, z = vertices[i]
            if y == front:
                keys["belly_out"][i] = (x, y - 0.05, z)
    return MeshData(vertices, faces, face_materials, groups, keys)


def blender_to_ue_cm(v: Sequence[float]) -> Vec:
    """FEV-confirmed mapping (H-axis): Blender world metres (x, y, z) -> UE component cm (x, -y, z) * 100."""
    return (v[0] * 100.0, -v[1] * 100.0, v[2] * 100.0)
