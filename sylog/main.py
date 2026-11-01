from contextlib import contextmanager
import os
from typing import Generator

from dotenv import load_dotenv
from nicegui import ui, app
from loguru import logger

import symhistory
import symlog
import symmanager
import symexport
import symheadtail
import store
import utils


load_dotenv()
utils.set_up_logger("./log")

DB = store.SqliteDB()
DB.open_db()


@contextmanager
def header_and_footer() -> Generator:
    # app.storage.user.clear()  # TODO: remove dev
    app.storage.user.setdefault("profile_id", 1)
    with symheadtail.content(DB):
        yield


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
    storage_secret=os.getenv("STORAGE_SECRET", None),
    viewport="width=device-width, initial-scale=1,maximum-scale=1",
    reload=True,
)
