import os

import requests
from flask import Flask, jsonify, send_from_directory

BASE = "https://footballcharts-backend.onrender.com/api/v1"
HERE = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)


@app.get("/")
def index():
    return send_from_directory(os.path.join(HERE, "static"), "index.html")


@app.get("/api/leagues")
def leagues():
    r = requests.get(f"{BASE}/leagues/", timeout=20)
    r.raise_for_status()
    return jsonify(r.json())


@app.get("/api/fixtures/<lig>")
def fixtures(lig):
    r = requests.get(f"{BASE}/leagues/{lig}/fixtures/", timeout=20)
    r.raise_for_status()
    out = []
    for m in r.json().get("matches", []):
        dc = m.get("model_predictions", {}).get("dc_v2", {})
        if not dc.get("gates", {}).get("probabilities"):
            continue
        raw = dc["raw"]
        out.append({
            "mac": f'{m["home_team"]} - {m["away_team"]}',
            "tarih": f'{m["match_date"]} {m["time"]} (UTC)',
            "model": {
                "1": raw["home"],
                "X": 1 - raw["home"] - raw["away"],
                "2": raw["away"],
            },
        })
    return jsonify(out)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
