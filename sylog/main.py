from contextlib import contextmanager

from nicegui import ui
from loguru import logger

import symhistory
import symlog
import symmanager
import symexport
import store
import utils

DB = store.SqliteDB()
DB.open_db()

utils.set_up_logger("./log")


@contextmanager
def header_and_footer():
    with ui.column().classes("w-full max-w-2xl mx-auto"):
        with ui.row().classes("w-full"):
            ui.button(
                icon="home",
                on_click=lambda: ui.navigate.to("/"),
            ).classes("w-12")
            ui.button(
                icon="share",
                on_click=lambda: ui.navigate.to("/export"),
            ).classes("ml-auto")
            ui.button(
                icon="settings",
                on_click=lambda: ui.navigate.to("/manage-symptoms"),
            ).classes("")
        yield

    ui.separator().classes("my-6")

    log_items_count = DB.select_items_count()
    with ui.row().classes("w-full justify-center mb-4"):
        ui.label(">>")
        ui.link("SyLog", "https://github.com/kamildemocko/sylog", new_tab=True)
        ui.label("|")
        ui.label(f"{log_items_count} symptoms logged")
        ui.label("<<")

        # ui.markdown(f"\>\> **SyLog** &nbsp;| &nbsp;{log_items_count} symptoms logged <<").classes("w-full text-center")


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


@ui.page("/export")
def export():
    with header_and_footer():
        with ui.column().classes("w-full max-w-2xl mx-auto"):
            symexport.content(DB)


logger.info("process start")

ui.run(
    title="Symptom Logger",
    viewport="width=device-width, initial-scale=1,maximum-scale=1",
    reload=True,
)
