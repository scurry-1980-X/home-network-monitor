import json
from datetime import datetime

from device_history import get_device_history


CONFIG_FILE = "alert_config.json"


def load_alert_config():
    with open(CONFIG_FILE, "r") as file:
        return json.load(file)


def should_send_offline_alert(mac_address):
    config = load_alert_config()

    if mac_address not in config["monitored_devices"]:
        return False

    history = get_device_history(mac_address)

    if history is None:
        return False

    if history["is_online"]:
        return False

    if history["alert_sent"]:
        return False

    last_seen = datetime.strptime(
        history["last_seen"],
        "%Y-%m-%d %H:%M:%S",
    )

    offline_minutes = (
        datetime.now() - last_seen
    ).total_seconds() / 60

    return offline_minutes >= config["offline_threshold_minutes"]


def should_send_recovery_alert(mac_address):
    config = load_alert_config()

    if mac_address not in config["monitored_devices"]:
        return False

    history = get_device_history(mac_address)

    if history is None:
        return False

    return history["is_online"] and history["alert_sent"]
