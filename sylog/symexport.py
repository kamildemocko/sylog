import csv
from dataclasses import fields, asdict
from pathlib import Path

import arrow
from loguru import logger
from nicegui import ui

import store
from models import HistoryItem


def content(db: store.SqliteDB) -> None:
    def export_csv() -> None:
        limit_count = None if limit.value == "ALL" else limit.value
        all_items = db.select_items(count=limit_count)
        if len(all_items) == 0:
            ui.notify("No items to export")
            return


        export_dir = Path("./exports")
        export_dir.mkdir(exist_ok=True)

        logger.info("starting export")
        ui.notify("Exporting CSV")

        ts = arrow.now().format("YYYY-MM-DDTHH-mm")
        export_file = export_dir.joinpath(f"{ts}_sylog_export.csv")

        with export_file.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(
                file,
                [f.name for f in fields(HistoryItem)],
                delimiter=","
            )
            writer.writeheader()
            writer.writerows(asdict(i) for i in all_items)

        logger.info("starting file download")
        ui.download.file(export_file)

    ui.markdown("## CSV Export").classes("w-full text-center")

    with ui.column().classes("w-full"):
        limit = ui.select([10, 25, 50, 100, 500, 1000, "ALL"], value=100, label="Number of exported values").classes("w-full")
        ui.button("Export CSV", on_click=export_csv).classes("w-full")
