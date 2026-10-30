# exchange-breach-sim

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
