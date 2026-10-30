#!/data/data/com.termux/files/usr/bin/bash
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
