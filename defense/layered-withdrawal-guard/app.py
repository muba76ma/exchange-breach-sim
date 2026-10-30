from flask import Flask, request, jsonify
import os, time, logging
from collections import defaultdict

app = Flask(__name__)
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")

_recent = defaultdict(list)
LARGE_THRESHOLD = 1.0
WINDOW          = 60
MAX_PER_WINDOW  = 2
SECOND_APPROVER = os.getenv("SECOND_APPROVER", "compliance-service")
TIMELOCK        = 5

@app.route("/internal/withdraw", methods=["POST"])
def withdraw():
    svc      = request.headers.get("X-Service-Identity", "")
    approver = request.headers.get("X-Second-Approval", "")
    body     = request.get_json() or {}
    amount   = float(body.get("amount", 0))
    now      = time.time()

    _recent[svc] = [t for t in _recent[svc] if now - t < WINDOW]
    if len(_recent[svc]) >= MAX_PER_WINDOW:
        logging.warning(f"velocity block svc={svc}")
        return jsonify({"error": "velocity limit"}), 429
    _recent[svc].append(now)

    if amount >= LARGE_THRESHOLD and approver != SECOND_APPROVER:
        logging.warning(f"missing 2nd approval svc={svc} amount={amount}")
        return jsonify({"error": "second approval required"}), 403

    logging.info(f"timelock {TIMELOCK}s svc={svc} amount={amount}")
    time.sleep(min(TIMELOCK, 1))
    return jsonify({"queued": True, "amount": amount, "timelock": TIMELOCK})

@app.route("/healthz")
def healthz():
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8091)
