from contextlib import contextmanager

from nicegui import ui, app

from store import SqliteDB
import utils

@contextmanager
def content(db: SqliteDB):
    available_profiles = db.select_profiles()

    with ui.column().classes("w-full max-w-2xl mx-auto"):
        with ui.row().classes("w-full items-center"):
            ui.button(
                icon="home",
                on_click=lambda: ui.navigate.to("/"),
            ).classes("w-12")
            ui.select(
                {p.id: p.name for p in available_profiles},
                value=app.storage.user["profile_id"],
                on_change=utils.change_profile,
            )
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

    log_items_count = db.select_items_count(app.storage.user["profile_id"])
    with ui.row().classes("w-full justify-center mb-4"):
        ui.label(">>")
        ui.link("SyLog", "https://github.com/kamildemocko/sylog", new_tab=True)
        ui.label("|")
        ui.label(f"v{utils.version()}")
        ui.label("|")
        ui.label(f"{log_items_count} symptoms logged")
        ui.label("<<")
