from flask import Flask, render_template, redirect, url_for
from scanner import get_devices_from_xml, run_nmap_scan

app = Flask(__name__)


@app.route("/")
def home():
    devices = get_devices_from_xml("/Users/owner/network-scan.xml")
    return render_template("index.html", devices=devices)


@app.route("/refresh", methods=["POST"])
def refresh():
    run_nmap_scan()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
