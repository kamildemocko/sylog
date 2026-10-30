from nicegui import ui

import store

_page_size: int = 10
_active_filter: str | None = None


@ui.refreshable
def content(db: store.SqliteDB) -> None:
    def set_page_size(e) -> None:
        global _page_size

        _page_size = e.value
        ui.notify(f"Page size set to {_page_size}")
        content.refresh()

    def remove_item(uid: int) -> None:
        db.remove_an_item(uid)
        ui.notify("Item removed")
        content.refresh()

    def set_filter(e) -> None:
        global _active_filter

        _active_filter = e.value if e.value else None

        ui.notify(f"History filter set to {_active_filter}")
        content.refresh()

    def show_controls() -> None:
        with ui.row().classes("w-full flex-nowrap"):
            (
                ui
                .select(
                    all_symptoms,
                    value=_active_filter.title() if _active_filter else None,
                    label="Filter symptom",
                    on_change=set_filter,
                    clearable=True)
                .classes("flex-1")
            )
            (
                ui
                .select([10, 25, 50, 100], value=_page_size, label="History items", on_change=set_page_size)
                .classes("w-28")
            )

    saved_items = db.select_items(
        _page_size,
        _active_filter.lower() if _active_filter else None
    )
    all_symptoms = db.select_all_symptoms()
    all_symptoms = sorted([s.title() for s in all_symptoms])

    ui.markdown("## History").classes("w-full text-center")

    if len(saved_items) == 0:
        ui.label("There are no logged items yet, add one?").classes("w-full text-center")
        show_controls()
        return

    for item in saved_items:
        with ui.column().classes("w-full gap-0"):
            with ui.row().classes("w-full items-center flex-nowrap"):
                ui.markdown(f"**{item.symptom.title()}**")
                stars = 3 if item.severity == "HIGH" else 2 if item.severity == "MEDIUM" else 1
                ui.rating(max=3, icon="circle", value=stars).classes("flex-1 min-w-12")
                ui.markdown(f"_{item.human_timestamp()}_").classes("ml-auto")

                ui.button(
                    icon="delete",
                    on_click=lambda _, uid=item.id: remove_item(uid),
                ).classes("w-8").props("color=red")

            with ui.row().classes("w-full items-center"):
                ui.markdown(f"Context: {item.description or 'No context'}")

            ui.separator()

    show_controls()
