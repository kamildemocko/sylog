from typing import Callable

from nicegui import ui
from nicegui import app

from models import QueryItemDaily
import store
import utils

def content(db: store.SqliteDB, on_saved: list[Callable] | None = None):
    inputs: dict[str, tuple[ui.radio, ui.textarea]] = {}

    def add_rating(title: str, ratings_str: str) -> None:
        nonlocal inputs

        ratings = ratings_str.split("|")
        with ui.column().classes("w-full"):
            with ui.element("fieldset").classes("w-full border border-gray-300 rounded-lg"):
                with ui.element("legend").classes("px-2"):
                    ui.html(title.title())

                rvalue = ui.radio(options=ratings, value=ratings[0]).classes("w-full flex flex-wrap justify-center").props("inline")
                note = ui.textarea(label="Note").props("rows=1 autogrow")

        inputs[title] = (rvalue, note)

    def complete() -> None:
        if not date_input.value:
            ui.notify("Please fill the date and time")
            return

        if not utils.validate_date_or_time(date_input.value):
            ui.notify("Please fill the date correctly")
            return

        ts = utils.create_timestampt_wo_time(date_input.value)
        already_in_db = db.select_dailies_by_timestamp(app.storage.user["profile_id"], ts)
        if len(already_in_db):
            ui.notify("This date already saved!")
            return

        items: list[QueryItemDaily] = []
        for title, (el_rvalue, el_note) in inputs.items():
            item = QueryItemDaily(
                timestamp=ts,
                name=title,
                rvalue=el_rvalue.value,
                note=el_note.value if el_note.value else None,
                profile_id=app.storage.user["profile_id"],
            )
            items.append(item)

        db.insert_dailies(items)

        if on_saved:
            [cb() for cb in on_saved]

        ui.notify("Saved")

    with ui.row().classes("w-full flex-nowrap"):
        d, _ = utils.get_date_and_time()

        with ui.input("Date", value=d).classes("flex-1") as date_input:
            with date_input.add_slot("append"):
                ui.icon("edit_calendar").classes("cursor-pointer")

        with ui.dialog() as date_dialog:
            with ui.card():
                ui.date().bind_value(date_input)
                ui.button("Done", on_click=date_dialog.close)

        date_input.on("click", date_dialog.open)

    with ui.row().classes("w-full"):
        all_dailysev = db.select_all_dailyseverities(app.storage.user["profile_id"])

        # ratings = "None|Mild|Moderate|Severe|Not sure"
        for dailysev in all_dailysev:
            add_rating(dailysev[1], dailysev[2])

        ui.button("Complete check-in", on_click=complete).classes("w-full")
