import bpy
import logging
import traceback


def show_exception(exc: Exception, message: str | None = None, operator=None, context=None, title: str = "mgtools: Error", level: str = "ERROR", popup: bool = True, report: bool = True, log: bool = True):
    """Consistent, user-visible exception reporting helper.

    - Logs the full traceback to console and the logging module when `log` is True.
    - Calls `operator.report({level}, short_message)` when `operator` is provided and `report` is True.
    - Shows a short popup via WindowManager when `popup` is True.

    Keep messages short for popups and send full details to the system console.
    """
    short = message or str(exc)
    # Log full traceback
    if log:
        logging.getLogger(__name__).error("%s\n%s", short, traceback.format_exc())
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
            logging.getLogger(__name__).warning("Failed to show popup for exception: %s", short)
