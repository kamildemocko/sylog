import arrow


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
