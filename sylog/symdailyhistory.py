from loguru import logger
from nicegui import ui, app

import store
from models import DailyItem
import utils


@ui.refreshable
def content(db: store.SqliteDB) -> None:
    app.storage.user.setdefault("page_size_daily", 10)

    def set_page_size(e) -> None:
        logger.info(f"setting history page size to {e.value}")

        app.storage.user["page_size_daily"] = e.value
        ui.notify(f"Page size set to {e.value}")
        content.refresh()

    def remove_item(ts: str) -> None:
        logger.info(f"removing symptom with timestamp={ts}")

        db.remove_a_daily(app.storage.user["profile_id"], ts)
        ui.notify("Item removed")
        content.refresh()

    def show_controls() -> None:
        with ui.row().classes("w-full flex-nowrap"):
            (
                ui
                .select(
                    [10, 25, 50, 100],
                    value=app.storage.user["page_size_daily"],
                    label="History items",
                    on_change=set_page_size
                )
                .classes("w-28 ml-auto")
            )

    saved_items = db.select_dailies(
        app.storage.user["profile_id"],
        app.storage.user["page_size_daily"],
    )
    all_dailysev = db.select_all_dailyseverities(app.storage.user["profile_id"])
    all_dailysev = sorted([s[1].title() for s in all_dailysev])

    if len(saved_items) == 0:
        logger.info("no history items to show")

        ui.label("There are no logged items yet, add one?").classes("w-full text-center")
        show_controls()
        return

    saved_items_grouped: dict[str, list[DailyItem]] = {}
    for si in saved_items:
        saved_items_grouped.setdefault(si.human_timestamp(), []).append(si)

    logger.info(f"showing {len(saved_items)} history items")

    for human_ts, group in saved_items_grouped.items():
        with ui.row().classes("w-full"):
            ui.markdown(f"_{human_ts}_").classes("mr-auto")
            ui.button(icon="delete", on_click=lambda _, ts=group[0].timestamp: utils.confirm_modal(
                f"Delete symptom from {human_ts}",
                lambda: remove_item(ts)
            )).classes("w-8")

        for item in group:
            with ui.column().classes("w-full gap-0"):
                with ui.row().classes("w-full items-center flex-nowrap"):
                    ui.markdown(f"**{item.name.title()}**")
                    ui.markdown(f"*» {item.rvalue}*")
                    ui.markdown(f"Note: {item.note or 'Without note'}").classes("ml-auto")

        ui.separator()

    show_controls()
