#!/data/data/com.termux/files/usr/bin/bash
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
