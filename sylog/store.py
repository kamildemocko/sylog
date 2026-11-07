import atexit
from pathlib import Path
import sqlite3

from loguru import logger

from models import HistoryItem, Profile, QueryItem

SCHEMA_VERSION = 3


class ConnectionAlreadyOpenedError(Exception): ...
class ConnectionNotOpened(Exception): ...


default_symptoms = [
    ("bloating | abdominal fullness",),
    ("visible abdominal swelling",),
    ("gas",),
    ("abdominal pain",),
    ("headache",),
    ("anal irritation",),
    ("genital irritation",),
    ("perineal irritation",),
    ("body redness | hives",),
    ("itching",),
    ("bad breath",),
    ("reflux | heartburn",),
    ("fatigue | low energy",),
]


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
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.conn.execute("PRAGMA journal_mode=WAL")
        atexit.register(self._close_db)

        self._init_db()

    def _close_db(self) -> None:
        if not self.conn:
            return

        self.conn.close()

    def is_healthy(self) -> bool:
        if self.conn is None:
            return False

        try:
            with sqlite3.connect(self.db_path, timeout=2) as conn:
                conn.execute("SELECT 1").fetchone()

            return True
        except sqlite3.Error as er:
            print(er)
            return False

    def _init_db(self) -> None:
        if not self.conn:
            raise ConnectionNotOpened

        version = self.conn.execute("PRAGMA user_version").fetchone()[0]
        if version == 0:
            self._create_and_seed()
            self.conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
            version = SCHEMA_VERSION

        migrations = {
            1: self._migrate_1_to_2,
            2: self._migrate_2_to_3,
        }

        while version < SCHEMA_VERSION:
            migrations[version]()
            version += 1
            self.conn.execute(f"PRAGMA user_version = {version}")

    def _migrate_1_to_2(self) -> None:
        if not self.conn:
            raise RuntimeError("no DB connection")

        logger.info("Migrating DB v1 to v2")
        self.conn.execute("CREATE INDEX idx_log_items_ts ON log_items(ts);")

    def _migrate_2_to_3(self) -> None:
        if not self.conn:
            raise RuntimeError("no DB connection")

        logger.info("Migrating DB v2 to v3")
        self.conn.executescript("""
            BEGIN;

            CREATE TABLE profiles (
            	id INTEGER PRIMARY KEY,
            	name TEXT NOT NULL UNIQUE,
            	created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            );

            INSERT INTO profiles (name)
            VALUES ("Default");

            ALTER TABLE log_items
            ADD COLUMN profile_id INTEGER REFERENCES profiles(id)
             ON DELETE CASCADE;

            UPDATE log_items
            SET profile_id = 1
            WHERE profile_id IS NULL;

            CREATE INDEX idx_log_items_profile_id ON log_items(profile_id);

            ALTER TABLE symptoms
            ADD COLUMN profile_id INTEGER REFERENCES profiles(id)
             ON DELETE CASCADE;

            CREATE INDEX idx_symptoms_profile_id ON symptoms(profile_id);

            UPDATE symptoms
            SET profile_id = 1
            WHERE profile_id IS NULL;

            COMMIT;
        """)

    def _create_and_seed(self) -> None:
        if not self.conn:
            raise ConnectionNotOpened

        table_symptoms_cr_query = """
        CREATE TABLE symptoms (
        	id INTEGER PRIMARY KEY,
            profile_id INTEGER references profiles(id) ON DELETE CASCADE,
        	name TEXT NOT NULL,
        	created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        );
        """

        table_symptoms_in_query = """
        INSERT INTO symptoms (name, profile_id) VALUES (?, 1);
        """

        table_profiles_query = """
        CREATE TABLE profiles (
        	id INTEGER PRIMARY KEY,
        	name TEXT NOT NULL UNIQUE,
        	created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        );
        """

        table_profiles_default_query = """
        INSERT INTO profiles (name)
        VALUES ('Default');
        """

        table_log_items_query = """
        CREATE TABLE log_items (
        	id INTEGER PRIMARY KEY,
            profile_id INTEGER references profiles(id) ON DELETE CASCADE,
        	ts TEXT,
        	symptom TEXT NOT NULL,
        	severity TEXT NOT NULL,
        	description TEXT NULL,
        	created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
        );
        """

        table_log_items_indexes_query = """
        CREATE INDEX idx_log_items_symptom ON log_items(symptom);
        CREATE INDEX idx_log_items_ts ON log_items(ts);
        CREATE INDEX idx_log_items_profile_id ON log_items(profile_id);
        CREATE INDEX idx_symptoms_profile_id ON symptoms(profile_id);
        """

        self.conn.execute(table_profiles_query)
        self.conn.execute(table_profiles_default_query)
        self.conn.commit()

        self.conn.execute(table_symptoms_cr_query)
        self.conn.executemany(table_symptoms_in_query, default_symptoms)
        self.conn.commit()

        self.conn.execute(table_log_items_query)
        self.conn.executescript(table_log_items_indexes_query)

    def select_all_symptoms(self, profile_id: int) -> list[str]:
        if not self.conn:
            raise ConnectionNotOpened

        query = """
        SELECT name FROM symptoms
        WHERE profile_id = ?
        LIMIT 100;
        """

        selected = self.conn.execute(query, (profile_id,)).fetchall()
        return [s[0] for s in selected]

    def insert_a_symptom(self, profile_id: int, name: str) -> None:
        if not self.conn:
            raise ConnectionNotOpened

        query = """
        INSERT INTO symptoms (name, profile_id) VALUES (?, ?);
        """

        self.conn.execute(query, (name.lower(), profile_id))
        self.conn.commit()

    def remove_a_symptom(self, profile_id: int, name: str) -> None:
        if not self.conn:
            raise ConnectionNotOpened

        query = """
        DELETE FROM symptoms WHERE name = ? AND profile_id = ?;
        """

        self.conn.execute(query, (name.lower(), profile_id))
        self.conn.commit()

    def count_symptoms(self, profile_id: int) -> int:
        if not self.conn:
            raise ConnectionNotOpened

        query = """
        SELECT COUNT(id) FROM symptoms WHERE profile_id = ?;
        """

        return self.conn.execute(query, (profile_id,)).fetchone()[0]

    def insert_an_item(self, item: QueryItem) -> None:
        if not self.conn:
            raise ConnectionNotOpened

        query = """
        INSERT INTO log_items (ts, symptom, severity, description, profile_id) VALUES (?, ?, ?, ?, ?);
        """

        self.conn.execute(query, (
            item.timestamp,
            item.symptom,
            item.severity,
            item.description,
            item.profile_id,
        ))
        self.conn.commit()

    def select_items(self, profile_id: int, count: int | None = 20, symptom_filter_value: str | None = None) -> list[HistoryItem]:
        if not self.conn:
            raise ConnectionNotOpened

        if count is None:
            count = -1

        query_all = """
        SELECT id, ts, symptom, severity, description
        FROM log_items
        WHERE profile_id = ?
        ORDER BY ts DESC
        LIMIT ?;
        """

        query_w_filter = """
        SELECT id, ts, symptom, severity, description
        FROM log_items
        WHERE symptom = ?
         AND profile_id = ?
        ORDER BY ts DESC
        LIMIT ?;
        """

        if symptom_filter_value:
            selected = self.conn.execute(query_w_filter, (symptom_filter_value, profile_id, count)).fetchall()
        else:
            selected = self.conn.execute(query_all, (profile_id, count,)).fetchall()

        return [HistoryItem(*s) for s in selected]

    def select_items_count(self, profile_id: int) -> int:
        if not self.conn:
            raise ConnectionNotOpened

        query_all = """
        SELECT count(id) FROM log_items WHERE profile_id = ?;
        """

        selected = self.conn.execute(query_all, (profile_id,)).fetchone()

        return int(selected[0])

    def remove_an_item(self, profile_id: int, uid: int) -> None:
        if not self.conn:
            raise ConnectionNotOpened

        query = """
        DELETE FROM log_items
        WHERE id = ?
         AND profile_id = ?;
        """

        self.conn.execute(query, (uid, profile_id))
        self.conn.commit()

    def change_an_item(
        self, profile_id: int, uid: int, new_severity: str, new_description: str | None
    ) -> None:
        if not self.conn:
            raise ConnectionNotOpened

        query = """
        UPDATE log_items
        SET severity = ?, description = ?
        WHERE id = ?
         AND profile_id = ?;
        """

        self.conn.execute(query, (new_severity, new_description, uid, profile_id))
        self.conn.commit()

    def select_profiles(self) -> list[Profile]:
        if not self.conn:
            raise ConnectionNotOpened

        query = """
        SELECT id, name FROM profiles;
        """

        profiles =  self.conn.execute(query).fetchall()
        return [Profile(*s) for s in profiles]

    def insert_profile(self, name: str) -> int:
        if not self.conn:
            raise ConnectionNotOpened

        insert_query = """
        INSERT INTO profiles (name) VALUES (?);
        """

        insert_default_symptoms_query = """
        INSERT INTO symptoms (name, profile_id) VALUES (?, ?);
        """

        cursor = self.conn.execute(insert_query, (name, ))
        lastid = cursor.lastrowid

        self.conn.executemany(insert_default_symptoms_query, [(s[0], lastid) for s in default_symptoms])

        self.conn.commit()

        return lastid or -1

    def remove_profile(self, uid: int) -> None:
        if not self.conn:
            raise ConnectionNotOpened

        query = """
        DELETE FROM profiles WHERE id = ?;
        """

        self.conn.execute(query, (uid, ))
        self.conn.commit()

    def update_profile_name(self, uid: int, new_name: str) -> None:
        if not self.conn:
            raise ConnectionNotOpened

        query = """
        UPDATE profiles
        SET name = ?
        WHERE id = ?;
        """

        self.conn.execute(query, (new_name, uid))
        self.conn.commit()

    def backup_database(self, dest_path: Path) -> None:
        if not self.conn:
            raise ConnectionNotOpened

        with sqlite3.connect(dest_path) as dest:
            self.conn.backup(dest)
