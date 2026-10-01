import json
import urllib.parse
import urllib.request


CONFIG_FILE = "pushover_config.json"
PUSHOVER_URL = "https://api.pushover.net/1/messages.json"


def load_pushover_config():
    with open(CONFIG_FILE, "r") as file:
        return json.load(file)


def send_notification(title, message):
    config = load_pushover_config()

    data = urllib.parse.urlencode(
        {
            "token": config["api_token"],
            "user": config["user_key"],
            "title": title,
            "message": message,
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        PUSHOVER_URL,
        data=data,
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=10) as response:
        return response.status == 200
