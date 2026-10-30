"""blender-addon: Blender Operator and menu entry for the example character export."""

from __future__ import annotations

from pathlib import Path

import bpy
from bpy.props import StringProperty

from .blender_export import export_character
from .spec import default_character


class EXCHAR_OT_export_character(bpy.types.Operator):
    bl_idname = "exchar.export_character"
    bl_label = "Export Example Character (.fbx)"
    bl_options = {"REGISTER"}

    directory: StringProperty(name="Output Directory", subtype="DIR_PATH")

    def execute(self, context):
        if not self.directory:
            self.report({"ERROR"}, "Output directory is required")
            return {"CANCELLED"}
        try:
            record = export_character(default_character(), Path(self.directory), context.scene)
        except (ValueError, RuntimeError, OSError) as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        self.report({"INFO"}, f"Exported {record['fbx']}")
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


def _menu(self, context):
    self.layout.operator(EXCHAR_OT_export_character.bl_idname, text="Example Character (.fbx)")


def register() -> None:
    bpy.utils.register_class(EXCHAR_OT_export_character)
    bpy.types.TOPBAR_MT_file_export.append(_menu)


def unregister() -> None:
    bpy.types.TOPBAR_MT_file_export.remove(_menu)
    bpy.utils.unregister_class(EXCHAR_OT_export_character)
