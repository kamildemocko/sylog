from nicegui import ui

import symhistory
import symlog
import store

DB = store.SqliteDB()
DB.open_db()


@ui.page("/")
def index():
    # TODO header
    # TODO symptoms adder

    with ui.column().classes("w-full max-w-2xl mx-auto"):
        symlog.content(DB, on_saved=symhistory.content.refresh)
        ui.separator().classes("my-6")
        symhistory.content(DB)

ui.run(title="Symptom Logger")
