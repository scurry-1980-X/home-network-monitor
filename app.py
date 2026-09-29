from flask import Flask, render_template, redirect, url_for, request
from scanner import get_devices_from_xml, run_nmap_scan

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
    devices = get_devices_from_xml("/Users/owner/network-scan.xml")

    privacy_mode = request.args.get("privacy") == "1"

    if privacy_mode:
        devices = apply_privacy_mode(devices)

    return render_template(
        "index.html",
        devices=devices,
        privacy_mode=privacy_mode
    )


@app.route("/refresh", methods=["POST"])
def refresh():
    run_nmap_scan()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)