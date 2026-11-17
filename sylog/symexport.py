import csv
from dataclasses import fields, asdict
from pathlib import Path
from tempfile import TemporaryDirectory

import arrow
from loguru import logger
from nicegui import ui, app

import store
from models import DailyItem, HistoryItem


def content(db: store.SqliteDB) -> None:
    def _write_csv(export_file: Path, all_items: list, fieldnames_class: type[HistoryItem] | type[DailyItem]) -> None:
        with export_file.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(
                file,
                [f.name for f in fields(fieldnames_class)],
                delimiter=","
            )
            writer.writeheader()
            writer.writerows(asdict(i) for i in all_items)

    def export_csv_symptoms() -> None:
        limit_count = None if limit_sym.value == "ALL" else limit_sym.value
        all_items = db.select_items(app.storage.user["profile_id"], count=limit_count)
        if len(all_items) == 0:
            ui.notify("No items to export")
            return

        export_dir = Path("./exports")
        export_dir.mkdir(exist_ok=True)

        logger.info("starting export")
        ui.notify("Exporting CSV")

        ts = arrow.now().format("YYYY-MM-DDTHH-mm")
        export_file = export_dir.joinpath(f"{ts}_user{app.storage.user['profile_id']}_sylog_symptoms_export.csv")

        _write_csv(export_file, all_items, HistoryItem)

        logger.info("starting file download")
        ui.download.file(export_file)

    def export_csv_dailies() -> None:
        limit_count = None if limit_day.value == "ALL" else limit_day.value
        all_items = db.select_dailies(app.storage.user["profile_id"], count=limit_count)
        if len(all_items) == 0:
            ui.notify("No items to export")
            return

        print(all_items)

        export_dir = Path("./exports")
        export_dir.mkdir(exist_ok=True)

        logger.info("starting export")
        ui.notify("Exporting CSV")

        ts = arrow.now().format("YYYY-MM-DDTHH-mm")
        export_file = export_dir.joinpath(f"{ts}_user{app.storage.user['profile_id']}_sylog_dailies_export.csv")

        _write_csv(export_file, all_items, DailyItem)

        logger.info("starting file download")
        ui.download.file(export_file)

    def backup_db() -> None:
        logger.info("starting db backup")

        with TemporaryDirectory() as tmp:
            tempfile = Path(tmp).joinpath("dbexport")
            db.backup_database(tempfile)
            backup_data = tempfile.read_bytes()

        ui.download.content(
            backup_data,
            filename="sylog_backup.db",
            media_type="application/octet-stream",
        )

        logger.info("starting DB backup download")
        ui.notify("starting DB backup download")

    ui.markdown("## Export Symptoms").classes("w-full text-center")

    with ui.column().classes("w-full"):
        limit_sym = ui.select([10, 25, 50, 100, 500, 1000, "ALL"], value=100, label="Number of exported values").classes("w-full")
        ui.button("Export CSV", on_click=export_csv_symptoms).classes("w-full")

    ui.separator()

    ui.markdown("## Export Dailies").classes("w-full text-center")

    with ui.column().classes("w-full"):
        limit_day = ui.select([10, 25, 50, 100, 500, 1000, "ALL"], value=100, label="Number of exported values").classes("w-full")
        ui.button("Export CSV", on_click=export_csv_dailies).classes("w-full")

    ui.separator()

    ui.markdown("## Database backup").classes("w-full text-center")

    with ui.column().classes("w-full"):
        ui.button("Backup Database", on_click = backup_db).classes("w-full")
