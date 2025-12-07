import os
import re
from flask import Flask, Response
import httpx

app = Flask(__name__)

API_KEY = os.environ.get("API_KEY")
DEVICE_IDS = []
DEVICE_NAMES = []
for d in os.environ.get("DEVICES").split(','):
    name = d.split(':')[0]
    dev_id = d.split(':')[1]
    DEVICE_IDS.append(dev_id)
    DEVICE_NAMES.append(name)

print("Devices:", list(zip(DEVICE_NAMES, DEVICE_IDS)))

SHELLY_HOST = os.environ.get("SHELLY_HOST")

def flatten_response(d: dict|list):
    metrics = dict()
    if isinstance(d, list):
        for i, x in enumerate(d):
            submetrics = flatten_response(x)
            for subk, subv in submetrics.items():
                metrics[f"{i}_{subk}"] = subv
    else:
        for k, v in d.items():
            k_name = re.sub(r"[^a-zA-Z0-9_-]", "-", k)
            if isinstance(v, dict):
                submetrics = flatten_response(v)
                for subk, subv in submetrics.items():
                    metrics[f"{k_name}_{subk}"] = subv
            else:
                try:
                    v = float(v)
                    metrics[k_name] = v
                except:
                    pass
    return metrics

@app.route("/metrics", methods=["GET"])
def metrics_endpoint():
    response = httpx.post(
        f"https://{SHELLY_HOST}/v2/devices/api/get?auth_key={API_KEY}",
        json={"ids": DEVICE_IDS, "select": ["status"]},
        timeout=10
    )
    data = response.json()
    lines = []
    for d_name, d in zip(DEVICE_NAMES, data):
        print(d_name, d)
        for m_name, m_value in flatten_response(d).items():
            lines.append(
                "shelly_"+m_name+"{name=\""+d_name+"\"} "+str(m_value)
            )
    return Response("\n".join(lines) + "\n", mimetype="text/plain")

if __name__ == "__main__":
    # Start Flask server
    app.run(host="0.0.0.0", port=9111)
