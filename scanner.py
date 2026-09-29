import json
import os
import subprocess
import threading
import xml.etree.ElementTree as ET

from device_history import get_device_history, update_device_history


XML_FILE = "/Users/owner/network-scan.xml"
TEMP_XML_FILE = "/Users/owner/network-scan.tmp.xml"
KNOWN_DEVICES_FILE = "known_devices.json"
LOCAL_CONFIG_FILE = "local_config.json"
NETWORK_SUBNET = os.getenv("NETWORK_SUBNET", "192.168.1.0/24")


def load_local_config():
    try:
        with open(LOCAL_CONFIG_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


LOCAL_CONFIG = load_local_config()

LOCAL_HOSTNAME = os.getenv(
    "LOCAL_HOSTNAME",
    LOCAL_CONFIG.get("local_hostname", "")
)

SCAN_LOCK = threading.Lock()


def run_nmap_scan():
    with SCAN_LOCK:
        subprocess.run(
            [
                "sudo",
                "-n",
                "/usr/local/bin/nmap",
                "-sn",
                "-oX",
                TEMP_XML_FILE,
                NETWORK_SUBNET,
            ],
            check=True,
        )

        ET.parse(TEMP_XML_FILE)
        os.replace(TEMP_XML_FILE, XML_FILE)


def load_known_devices():
    try:
        with open(KNOWN_DEVICES_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def get_devices_from_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    known_devices = load_known_devices()
    devices = []

    for host in root.findall("host"):
        status_element = host.find("status")

        if status_element is None:
            continue

        if status_element.get("state") != "up":
            continue

        ip_address = "Unknown"
        mac_address = "Unknown"

        for address in host.findall("address"):
            if address.get("addrtype") == "ipv4":
                ip_address = address.get("addr")
            elif address.get("addrtype") == "mac":
                mac_address = address.get("addr")

        hostname = "Unknown"
        hostname_element = host.find("hostnames/hostname")

        if hostname_element is not None:
            hostname = hostname_element.get("name")

        known_info = known_devices.get(mac_address)

        if known_info:
            display_name = known_info.get("name", hostname)
            device_type = known_info.get("type", "Unknown")
            is_known = True

        elif LOCAL_HOSTNAME and hostname.lower().startswith(
            LOCAL_HOSTNAME.lower()
        ):
            display_name = "Home Network Monitor iMac"
            device_type = "Computer"
            is_known = True

        else:
            display_name = hostname
            device_type = "Unknown"
            is_known = False

        devices.append(
            {
                "ip_address": ip_address,
                "mac_address": mac_address,
                "hostname": display_name,
                "device_type": device_type,
                "is_known": is_known,
                "status": "Online",
            }
        )

    for device in devices:
        history = get_device_history(device["mac_address"])

        if history:
            device["first_seen"] = history["first_seen"]
            device["last_seen"] = history["last_seen"]
            device["scan_count"] = history["scan_count"]
        else:
            device["first_seen"] = "Not recorded"
            device["last_seen"] = "Not recorded"
            device["scan_count"] = 0

    return devices


def scan_and_update_history():
    run_nmap_scan()
    devices = get_devices_from_xml(XML_FILE)
    update_device_history(devices)
    return get_devices_from_xml(XML_FILE)


if __name__ == "__main__":
    devices = scan_and_update_history()

    print("Home Network Monitor")
    print("-" * 100)

    for device in devices:
        trust = "Known" if device["is_known"] else "Unknown"

        print(
            f"{device['ip_address']:15} "
            f"{device['mac_address']:17} "
            f"{device['hostname']:25} "
            f"{device['device_type']:20} "
            f"{trust}"
        )
