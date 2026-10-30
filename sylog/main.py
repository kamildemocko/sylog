from contextlib import contextmanager

from nicegui import ui

import symhistory
import symlog
import symmanager
import store

DB = store.SqliteDB()
DB.open_db()


@contextmanager
def header_and_footer():
    with ui.column().classes("w-full max-w-2xl mx-auto"):
        with ui.row().classes("w-full"):
            ui.button(
                icon="home",
                on_click=lambda: ui.navigate.to("/"),
            ).classes("w-12")
            ui.button(
                icon="settings",
                on_click=lambda: ui.navigate.to("/manage-symptoms"),
            ).classes("ml-auto")
        yield

    ui.separator().classes("my-6")
    ui.markdown("2026 **SyLog**").classes("w-full text-center")


@ui.page("/")
def index():
    with header_and_footer():
        with ui.column().classes("w-full max-w-2xl mx-auto"):
            symlog.content(DB, on_saved=symhistory.content.refresh)
            ui.separator().classes("my-6")
            symhistory.content(DB)


@ui.page("/manage-symptoms")
def manage_symptoms():
    with header_and_footer():
        with ui.column().classes("w-full max-w-2xl mx-auto"):
            symmanager.content(DB)


ui.run(
    title="Symptom Logger",
    viewport="width=device-width, initial-scale=1,maximum-scale=1",
)
