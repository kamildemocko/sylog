from nicegui import ui

import store
import utils


@ui.refreshable
def content(db: store.SqliteDB):
    # TODO add history max results toggle

    saved_items = db.select_items(10)

    ui.markdown("## History").classes("w-full text-center")

    for item in saved_items:
        with ui.row().classes("w-full flex-nowrap"):
            ui.knob(min=0, max=3, value=utils.knob_value_from_severity(item.severity))
            ui.markdown(f"**{item.symptom.title()}**").classes("w-32")
            ui.separator().classes("mx-4").props("vertical")
            ui.markdown(f"{item.description}").classes("flex-1 min-w-0")
            ui.separator().classes("mx-4").props("vertical")
            ui.markdown(f"_{item.human_timestamp()}_").classes("w-25 text-right")
