import json
import os
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request

from scanner import get_dashboard_devices, scan_and_update_history


app = Flask(__name__)


def apply_privacy_mode(devices):
    private_devices = []
    phone_number = 0
    unknown_number = 0

    for device in devices:
        private_device = device.copy()

        # Mask personal or identifying device names.
        if private_device.get("device_type") == "Phone":
            phone_number += 1
            private_device["hostname"] = f"Known Phone {phone_number}"

        elif not private_device.get("is_known"):
            unknown_number += 1
            private_device["hostname"] = f"Unknown Device {unknown_number}"

        elif private_device.get("device_type") == "Router / Gateway":
            private_device["hostname"] = "Network Gateway"

        elif private_device.get("device_type") == "Computer":
            private_device["hostname"] = "Home Network Monitor"

        # Mask the final octet of the IP address.
        ip = private_device.get("ip_address", "Unknown")

        if ip != "Unknown":
            parts = ip.split(".")

            if len(parts) == 4:
                private_device["ip_address"] = (
                    f"{parts[0]}.{parts[1]}.{parts[2]}.XXX"
                )

        # Mask the final three groups of the MAC address.
        mac = private_device.get("mac_address", "Unknown")

        if mac != "Unknown":
            parts = mac.split(":")

            if len(parts) == 6:
                private_device["mac_address"] = ":".join(
                    parts[:3] + ["XX", "XX", "XX"]
                )

        private_devices.append(private_device)

    return private_devices


@app.route("/")
def home():
    devices = get_dashboard_devices()

    privacy_mode = request.args.get("privacy") == "1"

    if privacy_mode:
        devices = apply_privacy_mode(devices)

    last_scan = "No successful scan yet"

    if os.path.exists("last_scan.json"):
        try:
            with open("last_scan.json", "r") as file:
                raw_last_scan = json.load(file).get("last_scan")

                if raw_last_scan:
                    parsed_last_scan = datetime.strptime(
                        raw_last_scan,
                        "%Y-%m-%d %H:%M:%S",
                    )
                    last_scan = parsed_last_scan.strftime(
                        "%b %d, %I:%M %p"
                    ).replace(" 0", " ")
                else:
                    last_scan = "No successful scan yet"
        except (OSError, json.JSONDecodeError):
            last_scan = "Unavailable"

    monitoring_status = {
        "last_scan": last_scan,
        "scan_interval_minutes": 5,
        "offline_threshold_minutes": 15,
        "monitored_device": "Crawl Space Fan Smart Plug",
        "pushover_configured": os.path.exists("pushover_config.json"),
    }

    return render_template(
        "index.html",
        devices=devices,
        privacy_mode=privacy_mode,
        monitoring_status=monitoring_status
    )


@app.route("/refresh", methods=["POST"])
def refresh():
    scan_and_update_history()

    privacy_mode = request.form.get("privacy") == "1"

    if privacy_mode:
        return redirect(url_for("home", privacy=1))

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
