from nicegui import ui

import store
import utils

_page_size = 10


@ui.refreshable
def content(db: store.SqliteDB):
    def set_page_size(e):
        global _page_size

        _page_size = e.value
        content.refresh()

    saved_items = db.select_items(_page_size)

    ui.markdown("## History").classes("w-full text-center")

    for item in saved_items:
        with ui.row().classes("w-full flex-nowrap"):
            ui.knob(min=0, max=3, value=utils.knob_value_from_severity(item.severity))
            ui.markdown(f"**{item.symptom.title()}**").classes("w-32")
            ui.separator().classes("mx-4").props("vertical")
            ui.markdown(f"{item.description}").classes("flex-1 min-w-0")
            ui.separator().classes("mx-4").props("vertical")
            ui.markdown(f"_{item.human_timestamp()}_").classes("w-25 text-right")

    with ui.column().classes("w-full"):
        (
            ui.
            select([1, 2, 10, 25, 50, 100], value=_page_size, label="History items", on_change=set_page_size)
            .classes("w-28")
            .classes("ml-auto")
        )
