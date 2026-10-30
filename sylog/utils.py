from typing import Callable

import arrow
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
