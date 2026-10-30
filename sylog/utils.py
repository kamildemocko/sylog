from pathlib import Path
import sys
from typing import Callable

import arrow
from loguru import logger
from nicegui import ui


def get_date_and_time() -> tuple[str, str]:
    date_now = arrow.now().format("YYYY-MM-DD")
    time_now = arrow.now().format("HH:mm")

    return date_now, time_now


def validate_date_or_time(value: str) -> bool:
    def is_parseable(value: str) -> bool:
        try:
            arrow.get(value)
            return True

        except arrow.ParserError:
            return False

    return is_parseable(value) or is_parseable(f"2000-01-01T{value}")


def create_timestampt_utc(date: str, time: str) -> str:
    parsed = arrow.get(f"{date}T{time}").replace(tzinfo="local")
    utc = parsed.to("utc")
    return utc.isoformat(sep=" ")


def knob_value_from_severity(severity: str) -> int:
    match severity:
        case "LOW":
            return 1
        case "MEDIUM":
            return 2
        case "HIGH":
            return 3
        case _:
            raise NotImplementedError


def confirm_modal(message: str, callback: Callable) -> None:
    with ui.dialog() as dialog:
        with ui.card():
            ui.markdown(f"#### {message}").classes("w-full text-center")

            with ui.row().classes("w-full flex-nowrap"):
                ui.button("Cancel", on_click=dialog.close).classes("flex-1")
                ui.button("Yes", on_click=lambda: (dialog.close(), callback())).classes("flex-1")

    dialog.open()


def set_up_logger(log_dir: str):
    _log_dir = Path(log_dir)
    _log_dir.mkdir(exist_ok=True, parents=True)

    _log_info = _log_dir.joinpath("info.log").resolve()
    _log_err = _log_dir.joinpath("error.log").resolve()

    logger.remove()
    logger.add(
        sys.stdout,
        format="{module}:{function} - {message}",
        level="INFO",
    )
    logger.add(
        _log_info,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {module}:{function} - {message}",
        level="INFO",
        rotation="1 month",
        retention="12 months",
        backtrace=False,
        compression="zip",
    )
    logger.add(
        _log_err,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {module}:{function} - {message}",
        level="ERROR",
        rotation="1 month",
        retention="12 months",
        compression="zip",
    )
