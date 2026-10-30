from flask import Flask, request, jsonify
import os, logging, hashlib

app = Flask(__name__)
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")
ALLOWED = os.getenv("ALLOWED_SERVICE_CERT", "withdrawal-service")

@app.route("/sign", methods=["POST"])
def sign():
    svc = request.headers.get("X-Service-Identity", "")
    if svc != ALLOWED:
        return jsonify({"error": "unauthorized service"}), 403
    body = request.get_json() or {}
    fake_sig = hashlib.sha256(f"{body}".encode()).hexdigest()
    logging.info(f"HSM SIGNED amount={body.get('amount')} to={body.get('to')} sig={fake_sig}")
    return jsonify({"signed": True, "signature": fake_sig, "amount": body.get("amount")})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8082)
