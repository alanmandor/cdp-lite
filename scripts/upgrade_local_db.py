"""Back up and upgrade the existing local SQLite revenue schema."""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def main() -> None:
    database_path = Path(__file__).resolve().parents[1] / "cdp_lite.db"
    if not database_path.exists():
        raise SystemExit("Start the API first to create the database.")
    with sqlite3.connect(database_path) as connection:
        columns = {row[1] for row in connection.execute(
            "PRAGMA table_info(fact_customer_event)"
        )}
        if not columns:
            raise SystemExit("The event fact table does not exist.")
        missing = {"purchase_amount": "NUMERIC(12, 2)", "currency_code": "VARCHAR(3)"}
        missing = {name: kind for name, kind in missing.items() if name not in columns}
        if not missing:
            print("Database schema is already up to date.")
            return
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup_path = database_path.with_name(f"cdp_lite_backup_{timestamp}.db")
        with sqlite3.connect(backup_path) as backup:
            connection.backup(backup)
        with connection:
            for name, kind in missing.items():
                connection.execute(f"ALTER TABLE fact_customer_event ADD COLUMN {name} {kind}")
        print(f"Backup: {backup_path}")
        print(f"Added columns: {', '.join(missing)}")
        print("Existing facts retain NULL revenue values; no history was rewritten.")


if __name__ == "__main__":
    main()
