import sqlite3
from datetime import datetime


DATABASE_FILE = "device_history.db"


def initialize_database():
    with sqlite3.connect(DATABASE_FILE) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS devices (
                mac_address TEXT PRIMARY KEY,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                scan_count INTEGER NOT NULL DEFAULT 1
            )
            """
        )


def update_device_history(devices):
    initialize_database()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with sqlite3.connect(DATABASE_FILE) as connection:
        for device in devices:
            mac_address = device.get("mac_address", "Unknown")

            if mac_address == "Unknown":
                continue

            existing_device = connection.execute(
                """
                SELECT first_seen, scan_count
                FROM devices
                WHERE mac_address = ?
                """,
                (mac_address,),
            ).fetchone()

            if existing_device:
                first_seen, scan_count = existing_device

                connection.execute(
                    """
                    UPDATE devices
                    SET last_seen = ?, scan_count = ?
                    WHERE mac_address = ?
                    """,
                    (timestamp, scan_count + 1, mac_address),
                )
            else:
                connection.execute(
                    """
                    INSERT INTO devices (
                        mac_address,
                        first_seen,
                        last_seen,
                        scan_count
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    (mac_address, timestamp, timestamp, 1),
                )


def get_device_history(mac_address):
    initialize_database()

    with sqlite3.connect(DATABASE_FILE) as connection:
        row = connection.execute(
            """
            SELECT first_seen, last_seen, scan_count
            FROM devices
            WHERE mac_address = ?
            """,
            (mac_address,),
        ).fetchone()

    if row is None:
        return None

    return {
        "first_seen": row[0],
        "last_seen": row[1],
        "scan_count": row[2],
    }
