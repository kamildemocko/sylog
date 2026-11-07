from loguru import logger
from nicegui import ui, app

import store
import utils


@ui.refreshable
def content(db: store.SqliteDB) -> None:
    app.storage.user.setdefault("page_size", 10)
    app.storage.user.setdefault("active_filter", None)

    def set_page_size(e) -> None:
        logger.info(f"setting history page size to {e.value}")

        app.storage.user["page_size"] = e.value
        ui.notify(f"Page size set to {e.value}")
        content.refresh()

    def remove_item(uid: int) -> None:
        logger.info(f"removing symptom with id={uid}")

        db.remove_an_item(app.storage.user["profile_id"], uid)
        ui.notify("Item removed")
        content.refresh()

    def change_item(uid: int, cur_severity: str, cur_description: str) -> None:
        logger.info(f"changing symptom with id={uid}")

        def callback(new_severity: str, new_description: str | None) -> None:
            new_severity = new_severity.strip()
            new_description = new_description.strip() if new_description else None

            if not new_severity or (new_severity == cur_severity and new_description == cur_description):
                ui.notify("No change")
                return

            db.change_an_item(app.storage.user["profile_id"], uid, new_severity, new_description)
            ui.notify("Item changed")
            content.refresh()

        utils.modal_severity_description(cur_severity, cur_description, callback)

    def set_filter(e) -> None:
        app.storage.user["active_filter"] = e.value if e.value else None

        logger.info(f"setting filter to {app.storage.user["active_filter"]}")

        ui.notify(f"History filter set to {app.storage.user["active_filter"]}")
        content.refresh()

    def show_controls() -> None:
        with ui.row().classes("w-full flex-nowrap"):
            (
                ui
                .select(
                    all_symptoms,
                    value=app.storage.user["active_filter"].title() if app.storage.user["active_filter"] else None,
                    label="Filter symptom",
                    on_change=set_filter,
                    clearable=True)
                .classes("flex-1")
            )
            (
                ui
                .select(
                    [10, 25, 50, 100],
                    value=app.storage.user["page_size"],
                    label="History items",
                    on_change=set_page_size
                )
                .classes("w-28")
            )

    saved_items = db.select_items(
        app.storage.user["profile_id"],
        app.storage.user["page_size"],
        app.storage.user["active_filter"].lower() if app.storage.user["active_filter"] else None
    )
    all_symptoms = db.select_all_symptoms(app.storage.user["profile_id"])
    all_symptoms = sorted([s.title() for s in all_symptoms])

    ui.markdown("## History").classes("w-full text-center")

    if len(saved_items) == 0:
        logger.info("no history items to show")

        ui.label("There are no logged items yet, add one?").classes("w-full text-center")
        show_controls()
        return

    logger.info(f"showing {len(saved_items)} history items")

    for item in saved_items:
        with ui.column().classes("w-full gap-0"):
            with ui.row().classes("w-full items-center flex-nowrap"):
                ui.markdown(f"**{item.symptom.title()}**")
                stars = 3 if item.severity == "HIGH" else 2 if item.severity == "MEDIUM" else 1
                ui.rating(max=3, icon="circle", value=stars).classes("flex-1 min-w-12")
                ui.markdown(f"_{item.human_timestamp()}_").classes("ml-auto")

                with ui.dropdown_button(icon="menu", auto_close=True):
                    ui.item("Edit", on_click=lambda _, uid=item.id, sev=item.severity, des=item.description: change_item(uid, sev, des))
                    ui.item("Delete", on_click=lambda _, uid=item.id, ts=item.human_timestamp(): utils.confirm_modal(
                        f"Delete symptom from {ts}",
                        lambda: remove_item(uid)
                    ))

            with ui.row().classes("w-full items-center"):
                ui.markdown(f"Context: {item.description or 'No context'}")

            ui.separator()

    show_controls()
