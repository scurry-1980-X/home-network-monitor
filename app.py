from flask import Flask, render_template
from scanner import get_demo_devices

app = Flask(__name__)


@app.route("/")
def home():
    devices = get_demo_devices()
    return render_template("index.html", devices=devices)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
