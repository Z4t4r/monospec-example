"""Example character tools: build a procedural character in Blender 5.1 and export a UE5-ready FBX.

Blender add-on entry (Operator ``EXCHAR_OT_export_character``) plus a headless CLI
(``cli/export_character.py``). ``spec`` is importable without Blender.
"""

from __future__ import annotations

bl_info = {
    "name": "Example Character Tools",
    "author": "monospec-example",
    "version": (1, 0, 0),
    "blender": (5, 1, 0),
    "location": "File > Export > Example Character (.fbx)",
    "description": "Procedural example character with UE5-ready FBX export",
    "category": "Import-Export",
}


def register() -> None:
    from . import operators

    operators.register()


def unregister() -> None:
    from . import operators

    operators.unregister()
