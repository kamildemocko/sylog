from nicegui import ui

import store


def content(db: store.SqliteDB):
    ui.markdown("# Manage Symptoms").classes("w-full text-center")
