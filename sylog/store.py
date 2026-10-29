import atexit
from pathlib import Path
import sqlite3

from models import QueryItem


class ConnectionAlreadyOpenedError(Exception): ...
class ConnectionNotOpened(Exception): ...


class SqliteDB:
    def __init__(self) -> None:
        data_dir = Path("./data")
        data_dir.mkdir(exist_ok=True)

        self.db_path = data_dir.joinpath("sylog.db")
        self.conn: sqlite3.Connection | None = None

    def open_db(self) -> None:
        if self.conn:
            raise ConnectionAlreadyOpenedError

        self.conn = sqlite3.connect(self.db_path, timeout=10)
        self.conn.execute("PRAGMA journal_mode=WAL")
        atexit.register(self._close_db)

        self._init_db()

    def _close_db(self) -> None:
        if not self.conn:
            return

        self.conn.close()

    def _init_db(self) -> None:
        if not self.conn:
            raise ConnectionNotOpened

        version = self.conn.execute("PRAGMA user_version").fetchone()[0]
        if version == 0:
            self._create_and_seed()
            self.conn.execute("PRAGMA user_version = 1")

    def _create_and_seed(self) -> None:
        if not self.conn:
            raise ConnectionNotOpened

        table_symptoms_cr_query = """
        CREATE TABLE symptoms (
        	id INTEGER PRIMARY KEY,
        	name TEXT NOT NULL,
        	created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        );
        """

        table_log_items_query = """
        CREATE TABLE log_items (
        	id INTEGER PRIMARY KEY,
        	ts TEXT,
        	symptom TEXT NOT NULL,
        	symptom_type TEXT NOT NULL,
        	severity TEXT NOT NULL,
        	description TEXT NULL,
        	created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
        );
        """

        table_symptoms_in_query = """
        INSERT INTO symptoms (name) VALUES (?);
        """

        default_symptoms = [
            ("Bloating | abdominal fullness",),
            ("Visible abdominal swelling",),
            ("Gas",),
            ("Abdominal pain",),
            ("Headache",),
            ("Anal irritation",),
            ("Genital irritation",),
            ("Perineal irritation",),
            ("Body redness | hives",),
            ("Itching",),
            ("Bad breath",),
            ("Reflux | heartburn",),
            ("Fatigue | low energy",),
        ]

        self.conn.execute(table_symptoms_cr_query)
        self.conn.executemany(table_symptoms_in_query, default_symptoms)
        self.conn.commit()
        self.conn.execute(table_log_items_query)

    def select_all_symptoms(self) -> list[str]:
        if not self.conn:
            raise ConnectionNotOpened

        query = """
        SELECT name FROM symptoms;
        """

        selected = self.conn.execute(query).fetchmany(100)
        return [s[0] for s in selected]

    def insert_a_symptom(self, name: str) -> None:
        if not self.conn:
            raise ConnectionNotOpened

        query = """
        INSERT INTO symptoms (name) VALUES (?);
        """

        self.conn.execute(query, (name,))
        self.conn.commit

    def remove_a_symptom(self, name: str) -> None:
        if not self.conn:
            raise ConnectionNotOpened

        query = """
        DELETE FROM symptoms WHERE name = ?;
        """

        self.conn.execute(query, (name,))
        self.conn.commit

    def insert_an_item(self, item: QueryItem) -> None:
        if not self.conn:
            raise ConnectionNotOpened

        query = """
        INSERT INTO log_items (ts, symptom, symptom_type, severity, description) VALUES (?, ?, ?, ?, ?);
        """

        self.conn.execute(query, (
            item.timestamp,
            item.symptom,
            item.symptom_type,
            item.severity,
            item.description,
        ))
        self.conn.commit()

    def select_items(self, count: int = 20) -> list[QueryItem]:
        if not self.conn:
            raise ConnectionNotOpened

        query = """
        SELECT ts, symptom, symptom_type, severity, description
        FROM log_items
        ORDER BY id DESC
        LIMIT ?;
        """

        selected = self.conn.execute(query, (count,)).fetchmany(count)
        return [QueryItem(*s) for s in selected]
