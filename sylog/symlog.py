from collections.abc import Callable

from loguru import logger
from nicegui import ui

import models
import store
import utils

SYMPTOMS_INP_VALUES = ["S", "C"]
SEVERITIES = ["LOW", "MEDIUM", "HIGH"]


def content(db: store.SqliteDB, on_saved: Callable[[], None] | None = None):
    def reset_form() -> None:
        d, t = utils.get_date_and_time()
        date_input.value = d
        time_input.value = t
        severity.value = SEVERITIES[1]
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
        )

        logger.info(f"saving symptom {data.symptom} ({data.severity}) with desc {data.description}")

        db.insert_an_item(data)

        reset_form()
        if on_saved:
            on_saved()

        ui.notify("Saved")

    ui.markdown("## Log Symptom").classes("w-full text-center")

    with ui.row().classes("w-full flex-nowrap"):
        d, t = utils.get_date_and_time()

        date_input = ui.date_input(value=d).classes("flex-1")
        time_input = ui.time_input(value=t).classes("flex-1")

    with ui.row().classes("w-full flex-nowrap items-stretch"):
        all_symptoms = db.select_all_symptoms()
        all_symptoms = sorted([s.title() for s in all_symptoms])

        symptom_select = (ui
            .select(all_symptoms, with_input=True, value=all_symptoms[0])
            .classes("flex-1")
        )

    severity = (
        ui
        .toggle(SEVERITIES, value=SEVERITIES[1])
        .classes("w-full")
        .props("spread")
    )
    desc = ui.textarea(placeholder="Context").classes("w-full")

    ui.button("Save", on_click=save).classes("w-full")
