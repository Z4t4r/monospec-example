"""blender-isolated: acceptance probe for the example-character-tools add-on (Blender 5.1 --background).

Registers the production add-on from repos/, runs exchar.export_character(directory=...) in an empty scene,
unregisters it and writes addon_check.json. Not a business API.
"""

from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path

import bpy

REQUEST = json.loads(Path(sys.argv[sys.argv.index("--") + 1]).read_text(encoding="utf-8"))
OUT = Path(REQUEST["output"])


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    result = {"blender": bpy.app.version_string}
    try:
        sys.path.insert(0, REQUEST["project"])
        import example_character_tools as addon

        for obj in list(bpy.data.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        addon.register()
        result["registered"] = hasattr(bpy.ops.exchar, "export_character") and \
            "EXCHAR_OT_export_character" in dir(bpy.types)
        result["operator_status"] = sorted(bpy.ops.exchar.export_character(directory=str(OUT / "operator")))
        addon.unregister()
        result["unregistered"] = "EXCHAR_OT_export_character" not in dir(bpy.types)
        result["stage"] = "done"
    except (ImportError, RuntimeError, ValueError, AttributeError) as exc:
        result.update(stage="error", error_type=type(exc).__name__, error=str(exc), traceback=traceback.format_exc())
    (OUT / "addon_check.json").write_text(json.dumps(result, indent=1), encoding="utf-8")


main()
