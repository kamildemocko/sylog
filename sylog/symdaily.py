from nicegui import ui

import utils
import store

def content(db: store.SqliteDB):
    def add_rating(title: str, ratings_str: str) -> None:
        ratings = ratings_str.split("|")
        with ui.column().classes("w-full"):
            with ui.element("fieldset").classes("w-full border border-gray-300 rounded-lg"):
                with ui.element("legend").classes("px-2"):
                    ui.html(title.title())

                ui.radio(options=ratings, value=ratings[0]).classes("w-full flex flex-wrap justify-center").props("inline")
                ui.textarea(label="Note").props("rows=1 autogrow")

    with ui.row().classes("w-full flex-nowrap"):
        d, _ = utils.get_date_and_time()

        with ui.input("Date", value=d).classes("flex-1") as date_input:
            with date_input.add_slot("append"):
                ui.icon("edit_calendar").classes("cursor-pointer")

        with ui.dialog() as date_dialog:
            with ui.card():
                ui.date().bind_value(date_input)
                ui.button("Done", on_click=date_dialog.close)

        date_input.on("click", date_dialog.open)

    with ui.row().classes("w-full"):
        ratings = "None|Mild|Moderate|Severe|Not sure"
        add_rating("Bloating", ratings)
        add_rating("Gas", ratings[:-9])

        ui.button("Complete check-in").classes("w-full")
