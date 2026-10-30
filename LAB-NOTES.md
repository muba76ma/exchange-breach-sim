# LAB-NOTES — end-to-end walkthrough

## Vulnerable path (exchange/withdrawal-service + exchange/hsm-mock)

    $ python3 attacker/forge_withdrawal_request.py
    [*] Forging withdrawal: {'amount': '6.36', 'asset': 'BTC', 'to': 'bc1qattacker-demo-address', 'user_id': 'alice'}
    [+] HTTP 200: {"amount":"6.36","signature":"81adb0bb...","signed":true}

Server log:

    HSM SIGNED amount=6.36 to=bc1qattacker-demo-address sig=81adb0bb...

**Why it works**: HSM trusts `X-Service-Identity: withdrawal-service`. It does
not verify the caller's actual TLS cert, does not check user auth, does not
rate-limit, does not require a second approver, does not cap amount.

## Hardened path (defense/layered-withdrawal-guard)

Same forged request → **403 second approval required**

Add `X-Second-Approval: compliance-service` → **200 queued (5s timelock)**

Fire 3 in a row → **429 velocity limit** on the third.

## Detection coverage

| Layer | Control | Detects |
|---|---|---|
| Sigma | `sigma_forged_withdrawal.yml` | svc identity without gateway auth |
| YARA | `yara_eip7702.yar` | Sweeper contract bytecode |
| Guard | velocity + 2nd approval + timelock | The whole forged-request class |

## What would still be missed

The lab models **withdrawal authorization**. It does NOT model:
- On-chain mixing / Tornado (T+20m)
- Cross-chain bridge hops
- Stablecoin issuer freezing (T+6h)
- Attribution (T+72h)

Those need separate labs.
