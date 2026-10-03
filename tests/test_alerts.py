import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

from alerts import should_send_offline_alert


class TestAlerts(unittest.TestCase):

    @patch("alerts.get_device_history")
    @patch("alerts.load_alert_config")
    def test_offline_device_over_threshold_sends_alert(
        self,
        mock_config,
        mock_history,
    ):
        mac = "AA:BB:CC:DD:EE:FF"

        mock_config.return_value = {
            "monitored_devices": [mac],
            "offline_threshold_minutes": 15,
        }

        mock_history.return_value = {
            "is_online": False,
            "alert_sent": False,
            "last_seen": (
                datetime.now() - timedelta(minutes=20)
            ).strftime("%Y-%m-%d %H:%M:%S"),
        }

        result = should_send_offline_alert(mac)

        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
