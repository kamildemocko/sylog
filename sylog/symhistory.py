from nicegui import ui

import models
import utils


def content():
    example_data = models.DatabaseHistoryItem(
        timestamp="2026-10-28T20:08:00+0100",
        symptom="bloating",
        severity="MEDIUM",
        description="yeah man",
    )

    ui.markdown("## History").classes("w-full text-center")

    with ui.row().classes("w-full flex-nowrap"):
        ui.knob(min=0, max=3, value=utils.knob_value_from_severity(example_data.severity))
        ui.markdown(f"**{example_data.symptom.title()}**")
        ui.separator().classes("mx-4").props("vertical")
        ui.markdown(f"{example_data.description}").classes("flex-1")
        ui.separator().classes("mx-4").props("vertical")
        ui.markdown(f"_{example_data.human_timestamp()}_")

    with ui.row().classes("w-full flex-nowrap"):
        ui.knob(min=0, max=3, value=utils.knob_value_from_severity(example_data.severity))
        ui.markdown(f"**{example_data.symptom.title()}**")
        ui.separator().classes("mx-4").props("vertical")
        ui.markdown(f"{example_data.description}").classes("flex-1")
        ui.separator().classes("mx-4").props("vertical")
        ui.markdown(f"_{example_data.human_timestamp()}_")
