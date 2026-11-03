from contextlib import contextmanager

from nicegui import ui, app

from store import SqliteDB
import utils


def header(db: SqliteDB) -> None:
    available_profiles = db.select_profiles()
    if app.storage.user["profile_id"] not in  {p.id for p in available_profiles}:
        app.storage.user["profile_id"] = 1

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

@ui.refreshable
def footer(db: SqliteDB) -> None:
    with ui.column().classes("w-full max-w-2xl mx-auto"):
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


@contextmanager
def content(db: SqliteDB):
    header(db)
    yield
    footer(db)
