
from datetime import datetime


def get_demo_devices():
    return [
        {
            "ip_address": "192.168.1.10",
            "mac_address": "AA:BB:CC:DD:EE:01",
            "hostname": "iphone",
            "device_type": "Phone",
            "is_known": True,
            "status": "Online",
            "last_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        },
        {
            "ip_address": "192.168.1.20",
            "mac_address": "AA:BB:CC:DD:EE:02",
            "hostname": "chromebook",
            "device_type": "Computer",
            "is_known": True,
            "status": "Online",
            "last_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        },
        {
            "ip_address": "192.168.1.30",
            "mac_address": "AA:BB:CC:DD:EE:03",
            "hostname": "xbox",
            "device_type": "Game Console",
            	"is_known": True,
            "status": "Online",
            "last_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        },
{
    "ip_address": "192.168.1.45",
    "mac_address": "DE:AD:BE:EF:00:01",
    "hostname": "unknown-device",
    "device_type": "Unknown",
    "is_known": False,
    "status": "Online",
    "last_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
},
    ]

if __name__ == "__main__":
    devices = get_demo_devices()

    print("Home Network Monitor")
    print("-" * 60)

    for device in devices:
        print(
            f"{device['ip_address']:15} "
            f"{device['mac_address']:17} "
            f"{device['hostname']:20} "
            f"{device['status']}"
        )
