# Telemetry

All lab services log to stdout.

    docker compose logs -f withdrawal-service hsm-mock

To ship to a real backend, set OTEL_EXPORTER_OTLP_ENDPOINT in .env.
