from nicegui import ui

import symhistory
import symlog


@ui.page("/")
def index():
    with ui.column().classes("w-full max-w-2xl mx-auto"):
        symlog.content()
        ui.separator().classes("my-6")
        symhistory.content()

ui.run()
