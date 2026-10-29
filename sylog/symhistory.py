from nicegui import ui

import store
import utils


def content(db: store.SqliteDB):
    # TODO add history max results toggle

    saved_items = db.select_items(10)

    # example_data = models.QueryItem(
    #     timestamp="2026-10-28T20:08:00+0100",
    #     symptom="bloating",
    #     symptom_type="standard",
    #     severity="MEDIUM",
    #     description="yeah man",
    # )

    ui.markdown("## History").classes("w-full text-center")

    for item in saved_items:
        with ui.row().classes("w-full flex-nowrap"):
            ui.knob(min=0, max=3, value=utils.knob_value_from_severity(item.severity))
            ui.markdown(f"**{item.symptom.title()}**")
            ui.separator().classes("mx-4").props("vertical")
            ui.markdown(f"{item.description}").classes("flex-1")
            ui.separator().classes("mx-4").props("vertical")
            ui.markdown(f"_{item.human_timestamp()}_")
