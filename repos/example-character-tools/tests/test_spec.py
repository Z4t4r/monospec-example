"""Host CPython unit tests for example_character_tools.spec (no Blender)."""

from __future__ import annotations

import sys
import unittest
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from example_character_tools.spec import BoneSpec, blender_to_ue_cm, default_character, mesh_data  # noqa: E402


class SpecTests(unittest.TestCase):
    def test_default_character_shape(self) -> None:
        spec = default_character()
        spec.validate()
        self.assertEqual(len(spec.bones), 18)
        self.assertEqual([b.name for b in spec.bones if b.parent is None], ["root"])
        data = mesh_data(spec)
        self.assertEqual(len(data.vertices), 17 * 8)
        self.assertEqual(len(data.faces), 17 * 6)
        self.assertEqual(sorted(data.shape_keys), ["belly_out", "head_scale_up"])
        self.assertEqual(spec.action.length, 30)

    def test_shape_key_deltas(self) -> None:
        data = mesh_data(default_character())
        moved = [i for i, (a, b) in enumerate(zip(data.shape_keys["belly_out"], data.vertices)) if a != b]
        self.assertEqual(len(moved), 4)
        self.assertTrue(all(abs(data.vertices[i][1] - data.shape_keys["belly_out"][i][1] - 0.05) < 1e-12 for i in moved))

    def test_invalid_specs_raise(self) -> None:
        spec = default_character()
        with self.assertRaises(ValueError):
            replace(spec, bones=spec.bones + (BoneSpec("root", None, (0, 0, 0), (0, 0, 1), 0.0),)).validate()
        with self.assertRaises(ValueError):
            replace(spec, bones=spec.bones + (BoneSpec("extra_root", None, (0, 0, 0), (0, 0, 1), 0.0),)).validate()
        with self.assertRaises(ValueError):
            replace(spec, bones=(BoneSpec("child", "missing", (0, 0, 0), (0, 0, 1), 0.1),)).validate()

    def test_ue_mapping(self) -> None:
        self.assertEqual(blender_to_ue_cm((0.1, -0.2, 1.5)), (10.0, 20.0, 150.0))


if __name__ == "__main__":
    unittest.main()
