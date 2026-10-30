


#!/data/data/com.termux/files/usr/bin/bash
set -e
mkdir -p exchange/withdrawal-service exchange/hsm-mock exchange/ledger-db \
         exchange/frontend attacker defense/layered-withdrawal-guard \
         defense/detection-rules telemetry lab/mock-laptop

# ETHICS.md
cat > ETHICS.md << 'ENDOFFILE'
# ⚠️ ETHICS & LEGAL NOTICE
This repository is a defensive security research lab.
Rules of Use: authorized use only, fake data only, isolated network,
no weaponization, responsible disclosure.
ENDOFFILE

# README.md
cat > README.md << 'ENDOFFILE'
# exchange-breach-sim
A safe, purple-team simulation lab.
ENDOFFILE

echo "Rebuild skeleton done."
