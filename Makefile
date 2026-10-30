.PHONY: up down logs attack defend clean

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
	curl -s -X POST http://127.0.0.1:8091/internal/withdraw \
	  -H "Content-Type: application/json" \
	  -H "X-Service-Identity: withdrawal-service" \
	  -d "{\"amount\":\"6.36\",\"asset\":\"BTC\",\"to\":\"bc1qdemo\",\"user_id\":\"alice\"}"

clean:
	docker compose down -v
