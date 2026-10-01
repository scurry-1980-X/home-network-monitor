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
                scan_count INTEGER NOT NULL DEFAULT 1,
                is_online INTEGER NOT NULL DEFAULT 1,
                alert_sent INTEGER NOT NULL DEFAULT 0
            )
            """
        )

        columns = [
            row[1]
            for row in connection.execute(
                "PRAGMA table_info(devices)"
            ).fetchall()
        ]

        if "is_online" not in columns:
            connection.execute(
                """
                ALTER TABLE devices
                ADD COLUMN is_online INTEGER NOT NULL DEFAULT 1
                """
            )

        if "alert_sent" not in columns:
            connection.execute(
                """
                ALTER TABLE devices
                ADD COLUMN alert_sent INTEGER NOT NULL DEFAULT 0
                """
            )


def update_device_history(devices):
    initialize_database()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    detected_macs = {
        device.get("mac_address")
        for device in devices
        if device.get("mac_address")
        and device.get("mac_address") != "Unknown"
    }

    with sqlite3.connect(DATABASE_FILE) as connection:
        connection.execute(
            """
            UPDATE devices
            SET is_online = 0
            """
        )

        for mac_address in detected_macs:
            existing_device = connection.execute(
                """
                SELECT scan_count
                FROM devices
                WHERE mac_address = ?
                """,
                (mac_address,),
            ).fetchone()

            if existing_device:
                scan_count = existing_device[0]

                connection.execute(
                    """
                    UPDATE devices
                    SET last_seen = ?,
                        scan_count = ?,
                        is_online = 1
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
                        scan_count,
                        is_online
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (mac_address, timestamp, timestamp, 1, 1),
                )


def get_device_history(mac_address):
    initialize_database()

    with sqlite3.connect(DATABASE_FILE) as connection:
        row = connection.execute(
            """
            SELECT first_seen,
                   last_seen,
                   scan_count,
                   is_online,
                   alert_sent
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
        "is_online": bool(row[3]),
        "alert_sent": bool(row[4]),
    }


def get_all_device_history():
    initialize_database()

    with sqlite3.connect(DATABASE_FILE) as connection:
        rows = connection.execute(
            """
            SELECT mac_address,
                   first_seen,
                   last_seen,
                   scan_count,
                   is_online,
                   alert_sent
            FROM devices
            ORDER BY last_seen DESC
            """
        ).fetchall()

    return [
        {
            "mac_address": row[0],
            "first_seen": row[1],
            "last_seen": row[2],
            "scan_count": row[3],
            "is_online": bool(row[4]),
            "alert_sent": bool(row[5]),
        }
        for row in rows
    ]


def set_alert_sent(mac_address, alert_sent):
    initialize_database()

    with sqlite3.connect(DATABASE_FILE) as connection:
        connection.execute(
            """
            UPDATE devices
            SET alert_sent = ?
            WHERE mac_address = ?
            """,
            (1 if alert_sent else 0, mac_address),
        )


def get_alert_sent(mac_address):
    history = get_device_history(mac_address)

    if history is None:
        return False

    return history["alert_sent"]
