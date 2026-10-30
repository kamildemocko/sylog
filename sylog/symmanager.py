from nicegui import ui

import store
import utils


@ui.refreshable
def content(db: store.SqliteDB):
    all_symptoms = db.select_all_symptoms()
    all_symptoms = sorted([s.title() for s in all_symptoms])

    def add_new_symbol(value: str | None) -> None:
        if not value:
            return

        db.insert_a_symptom(value.strip())
        ui.notify(f"Symbol {value} added")
        content.refresh()

    def remove_symbol(value: str | None) -> None:
        if not value:
            return

        def removal() -> None:
            db.remove_a_symptom(value)
            ui.notify(f"Symbol {value} removed")
            content.refresh()

        utils.confirm_modal(f"Delete {value}?", removal)

    ui.markdown("## Add new symptom").classes("w-full text-center items-stretch")
    with ui.row().classes("w-full"):
        inp = ui.input(placeholder="Ex. Headache").classes("w-full")
        ui.button("Add symptom", on_click=lambda: add_new_symbol(inp.value)).classes("w-full")

    ui.separator().classes("my-6")

    ui.markdown("## Remove symptom").classes("w-full text-center items-stretch")
    with ui.row().classes("w-full"):
        rem = ui.select(sorted(all_symptoms), label="Select", with_input=True).classes("w-full")
        ui.button("Remove symptom", on_click=lambda: remove_symbol(rem.value)).classes("w-full")
