"""End-to-end integration tests for exchange-breach-sim.

Spins up the three Flask services as subprocesses, runs the forged-withdrawal
attack against both the vulnerable service and the hardened guard, and asserts
the expected differential behavior.
"""
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

HSM = "http://127.0.0.1:8082"
WS = "http://127.0.0.1:8081"
GUARD = "http://127.0.0.1:8091"


def _wait_for(url, timeout=15.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1) as r:
                if r.status == 200:
                    return
        except Exception:
            time.sleep(0.2)
    raise RuntimeError(f"service did not become healthy: {url}")


def _post(url, body, headers=None):
    headers = {"Content-Type": "application/json", **(headers or {})}
    req = urllib.request.Request(
        url, data=json.dumps(body).encode(), headers=headers, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())


@pytest.fixture(scope="session")
def stack():
    env = {**os.environ, "HSM_URL": HSM}
    procs = [
        subprocess.Popen(
            [sys.executable, str(ROOT / "exchange/hsm-mock/app.py")], env=env
        ),
        subprocess.Popen(
            [sys.executable, str(ROOT / "exchange/withdrawal-service/app.py")],
            env=env,
        ),
        subprocess.Popen(
            [sys.executable, str(ROOT / "defense/layered-withdrawal-guard/app.py")],
            env=env,
        ),
    ]
    try:
        _wait_for(f"{HSM}/healthz")
        _wait_for(f"{WS}/healthz")
        _wait_for(f"{GUARD}/healthz")
        yield
    finally:
        for p in procs:
            p.terminate()
        for p in procs:
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill()


# --- HSM mock ----------------------------------------------------------------

def test_hsm_accepts_trusted_service(stack):
    status, body = _post(
        f"{HSM}/sign",
        {"amount": "1.0", "asset": "BTC", "to": "bc1qtest"},
        {"X-Service-Identity": "withdrawal-service"},
    )
    assert status == 200
    assert body["signed"] is True
    assert body["amount"] == "1.0"


def test_hsm_rejects_untrusted_service(stack):
    status, body = _post(
        f"{HSM}/sign",
        {"amount": "1.0"},
        {"X-Service-Identity": "random-attacker"},
    )
    assert status == 403
    assert "unauthorized" in body["error"]


# --- Vulnerable service ------------------------------------------------------

def test_vulnerable_service_forwards_forged_request(stack):
    """The whole point: a forged request bearing only the service header gets signed."""
    status, body = _post(
        f"{WS}/internal/withdraw",
        {
            "amount": "6.36",
            "asset": "BTC",
            "to": "bc1qattacker-demo-address",
            "user_id": "alice",
        },
        {"X-Service-Identity": "withdrawal-service"},
    )
    assert status == 200
    assert body["signed"] is True
    assert body["amount"] == "6.36"


# --- Hardened guard ----------------------------------------------------------

def test_guard_blocks_without_second_approval(stack):
    status, body = _post(
        f"{GUARD}/internal/withdraw",
        {"amount": "6.36", "asset": "BTC", "to": "bc1qattacker", "user_id": "alice"},
        {"X-Service-Identity": "svc-test-block"},
    )
    assert status == 403
    assert "second approval" in body["error"]


def test_guard_allows_with_second_approval(stack):
    status, body = _post(
        f"{GUARD}/internal/withdraw",
        {"amount": "6.36", "asset": "BTC", "to": "bc1qdemo", "user_id": "alice"},
        {
            "X-Service-Identity": "svc-test-allow",
            "X-Second-Approval": "compliance-service",
        },
    )
    assert status == 200
    assert body["queued"] is True


def test_guard_enforces_velocity(stack):
    """3 rapid requests from the same service -> 200, 200, 429."""
    url = f"{GUARD}/internal/withdraw"
    body = {"amount": "2.0", "asset": "BTC", "to": "bc1qdemo", "user_id": "bob"}
    headers = {
        "X-Service-Identity": "svc-test-burst",
        "X-Second-Approval": "compliance-service",
    }
    codes = [_post(url, body, headers)[0] for _ in range(3)]
    assert codes == [200, 200, 429]

