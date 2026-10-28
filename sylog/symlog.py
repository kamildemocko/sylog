from nicegui import ui

import models
from utils import get_date_and_time
from utils import validate_date_or_time

SYMPTOMS_INP_VALUES = ["S", "C"]
SYMPTOMS = ["headache", "redness | itching", "bloating"]
SEVERITIES = ["LOW", "MEDIUM", "HIGH"]


def content():
    def reset_form() -> None:
        d, t = get_date_and_time()
        date_input.value = d
        time_input.value = t
        symptom_input.value = ""
        severity.value = SEVERITIES[1]
        desc.value = ""

    def save():
        if not date_input.value or not time_input.value:
            ui.notify("Please fill the date and time")
            return

        if not validate_date_or_time(date_input.value) or not validate_date_or_time(time_input.value):
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

        data = models.SavedData(
            date=date_input.value,
            time=time_input.value,
            symptom=symptom,
            severity=severity.value,
            description=desc.value,
        )

        # TODO handle data
        print(data)

        reset_form()
        ui.notify("Saved")

    ui.markdown("## Log Symptom").classes("w-full text-center")

    with ui.row().classes("w-full flex-nowrap"):
        d, t = get_date_and_time()

        date_input = ui.date_input(value=d).classes("flex-1")
        time_input = ui.time_input(value=t).classes("flex-1")

    with ui.row().classes("w-full flex-nowrap items-stretch"):
        symptom_inp_value = "S"

        symptom_select = (ui
            .select(sorted(s.title() for s in SYMPTOMS), with_input=True, value=SYMPTOMS[0].title())
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
