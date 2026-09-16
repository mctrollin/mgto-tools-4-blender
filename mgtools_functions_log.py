import bpy
import time
import traceback
from contextlib import contextmanager


@contextmanager
def log_timing(label: str):
    """Log the elapsed time for a block, including blocks that raise."""
    timer = time.perf_counter()
    try:
        yield
    finally:
        elapsed_ms = (time.perf_counter() - timer) * 1000.0
        print("[mgtools timing] {}: {:.2f} ms".format(label, elapsed_ms))


def show_exception(exc: Exception, message: str | None = None, operator=None, context=None, title: str = "mgtools: Error", level: str = "ERROR", popup: bool = True, report: bool = True, log: bool = True):
    """Consistent, user-visible exception reporting helper.

    - Logs the full traceback to Blender's system console when `log` is True.
    - Calls `operator.report({level}, short_message)` when `operator` is provided and `report` is True.
    - Shows a short popup via WindowManager when `popup` is True.

    Keep messages short for popups and send full details to the system console.
    """
    short = message or str(exc)
    # Log full traceback
    if log:
        print("[mgtools error] {}".format(short))
        traceback.print_exc()

    # Operator report (shows message in the Info header)
    try:
        if report and operator is not None:
            try:
                operator.report({level}, short)
            except Exception:
                pass
    except Exception:
        pass

    # Popup (keep short and informative)
    if popup:
        ctx = context or bpy.context
        try:
            def _draw(self, ctx):
                self.layout.label(text=short)
                self.layout.label(text="See system console for details.")
            ctx.window_manager.popup_menu(_draw, title=title, icon='ERROR')
        except Exception:
            print("[mgtools warning] Failed to show popup for exception: {}".format(short))
