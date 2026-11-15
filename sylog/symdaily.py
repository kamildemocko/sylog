from nicegui import ui

import store

def content(db: store.SqliteDB):
    ui.label("TODO")
