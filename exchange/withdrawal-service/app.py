from flask import Flask, request, jsonify
import os, requests, logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")
HSM_URL = os.getenv("HSM_URL", "http://hsm-mock:8082")

@app.route("/internal/withdraw", methods=["POST"])
def internal_withdraw():
    svc = request.headers.get("X-Service-Identity", "unknown")
    body = request.get_json() or {}
    logging.info(f"withdraw request svc={svc} body={body}")
    r = requests.post(f"{HSM_URL}/sign", json=body,
                      headers={"X-Service-Identity": svc}, timeout=5)
    return jsonify(r.json()), r.status_code

@app.route("/healthz")
def healthz():
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
