from collections.abc import Callable

from loguru import logger
from nicegui import ui, app
from nicegui.events import ValueChangeEventArguments

import models
import store
import utils


def content(db: store.SqliteDB, on_saved: list[Callable] | None = None):
    def reset_form() -> None:
        d, t = utils.get_date_and_time()
        date_input.value = d
        time_input.value = t
        desc.value = ""

    def save():
        if not date_input.value or not time_input.value:
            ui.notify("Please fill the date and time")
            return

        if not utils.validate_date_or_time(date_input.value) or not utils.validate_date_or_time(time_input.value):
            ui.notify("Please fill the date and time correctly")
            return

        if not isinstance(symptom_select.value, str) or not symptom_select.value:
            ui.notify("Please select the symptom")
            return

        if not isinstance(severity.value, str) or not symptom_select.value:
            ui.notify("Please select the severity of the symptom")
            return

        data = models.QueryItem(
            timestamp=utils.create_timestampt_utc(date_input.value, time_input.value),
            symptom=symptom_select.value.lower(),
            severity=severity.value,
            description=desc.value if desc.value else None,
            profile_id=app.storage.user["profile_id"],
        )

        logger.info(f"saving symptom {data.symptom} ({data.severity}) with desc {data.description}")

        db.insert_an_item(data)

        reset_form()
        if on_saved:
            [cb() for cb in on_saved]

        ui.notify("Saved")

    def severity_for(name: str) -> list[str]:
        severities_raw = db.select_symptoms_severities(
            app.storage.user["profile_id"],
            name.lower()
        )
        if severities_raw is None:
            return []

        return severities_raw.split("|")

    def on_symptom_change(e: ValueChangeEventArguments) -> None:
        severities = severity_for(e.value)
        severity.set_options(severities, value=severities[1])


    with ui.row().classes("w-full flex-nowrap"):
        d, t = utils.get_date_and_time()

        with ui.input("Date", value=d).classes("flex-1") as date_input:
            with date_input.add_slot("append"):
                ui.icon("edit_calendar").classes("cursor-pointer")

        with ui.dialog() as date_dialog:
            with ui.card():
                ui.date().bind_value(date_input)
                ui.button("Done", on_click=date_dialog.close)

        date_input.on("click", date_dialog.open)

        with ui.input("Time", value=t).classes("flex-1") as time_input:
            with time_input.add_slot("append"):
                ui.icon("access_time").classes("cursor-pointer")

        with ui.dialog() as time_dialog:
            with ui.card():
                ui.time().bind_value(time_input)
                ui.button("Done", on_click=time_dialog.close)

        time_input.on("click", time_dialog.open)

    with ui.row().classes("w-full flex-nowrap items-stretch"):
        all_symptoms = db.select_all_symptoms(app.storage.user["profile_id"])
        all_symptoms = sorted([s.title() for s in all_symptoms])

        symptom_select = (ui
            .select(
                all_symptoms,
                with_input=True,
                value=all_symptoms[0],
                on_change=on_symptom_change
            ).classes("flex-1")
        ).props("behavior=menu")

    initial_severities = severity_for(all_symptoms[0])
    severity = (
        ui
        .toggle(initial_severities, value=initial_severities[1])
        .classes("w-full")
        .props("spread")
    )
    desc = ui.textarea(placeholder="Context").classes("w-full")

    ui.button("Save", on_click=save).classes("w-full")
