import json
import time
from datetime import datetime

from alerts import (
    load_alert_config,
    should_send_offline_alert,
    should_send_recovery_alert,
)
from device_history import set_alert_sent
from pushover import send_notification
from scanner import scan_and_update_history


SCAN_INTERVAL_SECONDS = 300
KNOWN_DEVICES_FILE = "known_devices.json"


def load_known_devices():
    with open(KNOWN_DEVICES_FILE, "r") as file:
        return json.load(file)


def check_alerts():
    config = load_alert_config()
    known_devices = load_known_devices()

    for mac_address in config["monitored_devices"]:
        device = known_devices.get(mac_address, {})
        device_name = device.get("name", mac_address)

        if should_send_offline_alert(mac_address):
            success = send_notification(
                "Network Device Offline",
                (
                    f"{device_name} has been offline for at least "
                    f"{config['offline_threshold_minutes']} minutes."
                ),
            )

            if success:
                set_alert_sent(mac_address, True)
                print(f"Outage alert sent: {device_name}")

        elif should_send_recovery_alert(mac_address):
            success = send_notification(
                "Network Device Recovered",
                f"{device_name} is back online.",
            )

            if success:
                set_alert_sent(mac_address, False)
                print(f"Recovery alert sent: {device_name}")


def run_monitor():
    print("Home Network Monitor started.")
    print("Automatic scan interval: 5 minutes")

    while True:
        try:
            print(
                f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                "Running network scan..."
            )

            devices = scan_and_update_history()

            print(
                f"Scan complete. {len(devices)} dashboard devices."
            )

            check_alerts()

        except Exception as error:
            print(f"Monitor cycle failed: {error}")

        time.sleep(SCAN_INTERVAL_SECONDS)


if __name__ == "__main__":
    run_monitor()
