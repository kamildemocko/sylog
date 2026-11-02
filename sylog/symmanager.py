from loguru import logger
from nicegui import ui, app

import store
import utils


@ui.refreshable
def content(db: store.SqliteDB):
    all_symptoms = db.select_all_symptoms(app.storage.user["profile_id"])
    all_symptoms = sorted([s.title() for s in all_symptoms])

    def add_new_symbol(value: str | None) -> None:
        if not value:
            return

        logger.info(f"adding new symbol {value}")

        db.insert_a_symptom(app.storage.user["profile_id"], value.strip())
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
        ui.button("Add symptom", on_click=lambda: add_new_symbol(add_sym.value)).classes("w-full")

    with ui.row().classes("w-full"):
        rem_sym = ui.select(sorted(all_symptoms), label="Remove as symptom", with_input=True).classes("w-full")
        ui.button("Remove symptom", on_click=lambda: remove_symbol(rem_sym.value)).classes("w-full")

    ui.separator().classes("my-6")

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

    ui.markdown("## Profiles").classes("w-full text-center items-stretch")

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
