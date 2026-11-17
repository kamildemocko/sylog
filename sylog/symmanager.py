from loguru import logger
from nicegui import ui, app

import store
import utils


@ui.refreshable
def content(db: store.SqliteDB):
    ui.markdown("## Dark Mode").classes("w-full text-center items-stretch")

    def set_light_or_dark(e) -> None:
        if e.value == "DARK":
            dark.enable()
            app.storage.user["dark_mode"] = True
        else:
            dark.disable()
            app.storage.user["dark_mode"] = False

    with ui.row().classes("w-full"):
        dark = ui.dark_mode(app.storage.user["dark_mode"])

        (
            ui
            .toggle(["LIGHT", "DARK"], value="DARK" if app.storage.user["dark_mode"] else "LIGHT", on_change=set_light_or_dark)
            .classes("w-full")
            .props("spread")
        )

    ui.separator().classes("my-6")

    all_symptoms = db.select_all_symptoms(app.storage.user["profile_id"])
    all_symptoms = sorted([s.title() for s in all_symptoms])

    def add_new_symbol(value: str | None, severities: list[str | None]) -> None:
        if not value:
            ui.notify("Please name the symptom")
            return

        severities_nn = [s for s in severities if s]
        severities_nn = [s.replace("|", "/") for s in severities_nn]

        if len(severities_nn) != 3:
            ui.notify("Please correct severity values")
            return

        logger.info(f"adding new symbol {value}")

        db.insert_a_symptom(
            app.storage.user["profile_id"],
            value.strip(),
            "|".join(severities_nn)
        )
        ui.notify(f"Symbol {value} added")
        content.refresh()

    def remove_symbol(value: str | None) -> None:
        if not value:
            return

        def removal() -> None:
            logger.warning(f"removing symbol {value}")

            db.remove_a_symptom(app.storage.user["profile_id"], value)
            ui.notify(f"Symbol {value} removed")
            content.refresh()

        symptoms_count = db.count_symptoms(app.storage.user["profile_id"])
        if symptoms_count <= 1:
            ui.notify("You cannot delete all symbols, at least one must remain")
            return

        utils.confirm_modal(f"Delete {value}?", removal)

    ui.markdown("## Symptoms").classes("w-full text-center items-stretch")

    with ui.row().classes("w-full"):
        add_sym = ui.input(placeholder="Add new symptom, e.g. Headache").classes("w-full")
        with ui.row().classes("w-full flex-nowrap"):
            sev1 = ui.input(placeholder="Severity 1").classes("flex-1")
            sev2 = ui.input(placeholder="Severity 2").classes("flex-1")
            sev3 = ui.input(placeholder="Severity 3").classes("flex-1")

        ui.button(
            "Add symptom",
            on_click=lambda: add_new_symbol(
                add_sym.value,
                [sev1.value, sev2.value, sev3.value],
            )
        ).classes("w-full")

    with ui.row().classes("w-full"):
        rem_sym = ui.select(sorted(all_symptoms), label="Remove symptom", with_input=True).classes("w-full")
        ui.button("Remove symptom", on_click=lambda: remove_symbol(rem_sym.value)).classes("w-full")

    ui.separator().classes("my-6")

    ui.markdown("## Dailies").classes("w-full text-center items-stretch")

    daily_severity_values: list[str] = []
    all_dailysev = db.select_all_dailyseverities(app.storage.user["profile_id"])
    all_dailysev = sorted([s[1].title() for s in all_dailysev])

    @ui.refreshable
    def dynamic_daily_severities() -> None:
        for i, value in enumerate(daily_severity_values):
            if i > 5:
                ui.notify("Max amount of severities is 6")
                return

            ui.input(
                value=value,
                placeholder=f"Severity {i + 1}",
                on_change=lambda e, i=i: daily_severity_values.__setitem__(i, str(e.value)),
            ).classes("grow min-w-32")

    def add_daily_severity_input() -> None:
        daily_severity_values.append("")
        dynamic_daily_severities.refresh()

    def add_new_dailyseverity(name: str | None, severities: list[str]) -> None:
        if not name:
            ui.notify("Please name the daily")
            return

        if len(severities) < 2 or len(severities) > 6 or not all(severities):
            ui.notify("Please correct severity values")
            return

        db.insert_dailyseverity(
            app.storage.user["profile_id"],
            name,
            "|".join(severities),
        )

        ui.notify("Saved")
        content.refresh()

    def remove_dailyseverity(value: str | None) -> None:
        if not value:
            return

        def removal() -> None:
            logger.warning(f"removing daily severity {value}")

            db.remove_dailyseverity(app.storage.user["profile_id"], value.lower())
            ui.notify(f"Daily severity {value} removed")
            content.refresh()

        dailyseverities_count = db.count_dailyseverities(app.storage.user["profile_id"])
        if dailyseverities_count <= 1:
            ui.notify("You cannot delete all daily severities, at least one must remain")
            return

        utils.confirm_modal(f"Delete {value}?", removal)

    with ui.row().classes("w-full"):
        add_day = ui.input(placeholder="Add new daily, e.g. Rash").classes("w-full")

        with ui.row().classes("w-full flex-wrap items-stretch"):
            add_daily_severity_input()
            add_daily_severity_input()
            dynamic_daily_severities()

            ui.button(icon="add", on_click=add_daily_severity_input).classes("w-8")

        ui.button(
            "Add daily",
            on_click=lambda: add_new_dailyseverity(
                add_day.value,
                daily_severity_values,
            )
        ).classes("w-full")

    with ui.row().classes("w-full"):
        rem_day = ui.select(sorted(all_dailysev), label="Remove daily", with_input=True).classes("w-full")
        ui.button("Remove daily", on_click=lambda: remove_dailyseverity(rem_day.value)).classes("w-full")

    ui.separator().classes("my-6")

    ui.markdown("## Profiles").classes("w-full text-center items-stretch")

    def add_profile(name: str | None) -> None:
        if not name:
            return

        _ = db.insert_profile(name)
        ui.notify(f"Profile {name} created")
        ui.navigate.to("/manage-symptoms")

    def remove_profile(uid: int) -> None:
        if not uid:
            return

        if uid == 1:
            ui.notify("Cannot remove default profile")
            return

        _ = db.remove_profile(uid)
        app.storage.user["profile_id"] = 1

        ui.notify("Removed profile")
        ui.navigate.to("/manage-symptoms")

    def rename_profile(uid: int, new_name: str | None) -> None:
        new_name = new_name.strip() if new_name else ""

        if not uid or not new_name:
            return

        db.update_profile_name(uid, new_name)
        ui.notify(f"Profile renamed to {new_name}")
        ui.navigate.to("/manage-symptoms")

    with ui.row().classes("w-full"):
        add_pro = ui.input(placeholder="Add new profile").classes("w-full")
        ui.button("Add profile", on_click=lambda: add_profile(add_pro.value)).classes("w-full")

    available_profiles = db.select_profiles()

    with ui.row().classes("w-full"):
        rem_pro = ui.select(
            {p.id: p.name for p in available_profiles},
            label="Remove profile",
            with_input=True
        ).classes("w-full")
        ui.button("Remove profile", on_click=lambda: remove_profile(rem_pro.value)).classes("w-full")

    with ui.row().classes("w-full"):
        ren_pro = ui.select(
            {p.id: p.name for p in available_profiles},
            label="Rename profile",
            with_input=True
        ).classes("w-full")
        ren_pro_to = ui.input(label="Rename to").classes("w-full")
        ui.button(
            "Rename profile",
            on_click=lambda: rename_profile(ren_pro.value, ren_pro_to.value)
        ).classes("w-full")

    ui.separator().classes("my-6")
