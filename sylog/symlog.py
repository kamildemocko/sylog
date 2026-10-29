from nicegui import ui

import models
import store
import utils

SYMPTOMS_INP_VALUES = ["S", "C"]
SEVERITIES = ["LOW", "MEDIUM", "HIGH"]


def content(db: store.SqliteDB):
    def reset_form() -> None:
        d, t = utils.get_date_and_time()
        date_input.value = d
        time_input.value = t
        symptom_input.value = ""
        severity.value = SEVERITIES[1]
        desc.value = ""

    def save():
        if not date_input.value or not time_input.value:
            ui.notify("Please fill the date and time")
            return

        if not utils.validate_date_or_time(date_input.value) or not utils.validate_date_or_time(time_input.value):
            ui.notify("Please fill the date and time correctly")
            return

        symptom = (
            symptom_input.value
            if current_symptom_inp.value == "C"
            else symptom_select.value
        )

        if not isinstance(symptom, str) or not symptom.strip():
            ui.notify("Please select or fill the symptom")
            return

        data = models.QueryItem(
            timestamp=utils.create_timestampt_utc(date_input.value, time_input.value),
            symptom=symptom,
            symptom_type="standard" if current_symptom_inp.value == "S" else "custom",
            severity=severity.value,
            description=desc.value if desc.value else None,
        )

        db.insert_an_item(data)

        reset_form()
        ui.notify("Saved")

    ui.markdown("## Log Symptom").classes("w-full text-center")

    with ui.row().classes("w-full flex-nowrap"):
        d, t = utils.get_date_and_time()

        date_input = ui.date_input(value=d).classes("flex-1")
        time_input = ui.time_input(value=t).classes("flex-1")

    with ui.row().classes("w-full flex-nowrap items-stretch"):
        symptom_inp_value = "S"
        all_symptoms = db.select_all_symptoms()

        symptom_select = (ui
            .select(sorted(all_symptoms), with_input=True, value=all_symptoms[0])
            .classes("flex-1")
        )
        symptom_input = ui.input(placeholder="Custom symptom").classes("flex-1")

        current_symptom_inp = ui.toggle(SYMPTOMS_INP_VALUES, value=symptom_inp_value)
        symptom_select.bind_visibility_from(current_symptom_inp, "value", value="S")
        symptom_input.bind_visibility_from(current_symptom_inp, "value", value="C")

    severity = (
        ui
        .toggle(SEVERITIES, value=SEVERITIES[1])
        .classes("w-full")
        .props("spread")
    )
    desc = ui.textarea(placeholder="Description").classes("w-full")

    ui.button("Save", on_click=save).classes("w-full")
