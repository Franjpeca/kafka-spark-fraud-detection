#!/usr/bin/env bash
set -e

# -------------------------------------------------------------------
# Cargar variables de entorno desde .env
# -------------------------------------------------------------------
ENV_FILE="$(dirname "$0")/../.env"
if [[ -f "$ENV_FILE" ]]; then
  export $(grep -v '^#' "$ENV_FILE" | xargs)
fi

# -------------------------------------------------------------------
# Obtener broker de KAFKA_ADVERTISED_LISTENERS
# -------------------------------------------------------------------

if [[ -z "$KAFKA_ADVERTISED_LISTENERS" ]]; then
  echo "Error: KAFKA_ADVERTISED_LISTENERS no definido en .env"
  exit 1
fi

# Quita prefijo PLAINTEXT:// si existe
BROKER=${KAFKA_ADVERTISED_LISTENERS#*://}

TOPICS=(
  paysim_cash_in
  paysim_cash_out
  paysim_payment
  paysim_transfer
  paysim_debit
)

echo "== Limpiando mensajes Kafka (DEV) =="
echo "Usando broker: $BROKER"

for TOPIC in "${TOPICS[@]}"; do
  echo "Limpiando $TOPIC"

  # Cambia la retencion para que se eliminen
  docker exec kafka \
    kafka-configs \
    --bootstrap-server "$BROKER" \
    --entity-type topics \
    --entity-name "$TOPIC" \
    --alter \
    --add-config retention.ms=1000

  sleep 2

  # Quita la configuración para volver a default
  docker exec kafka \
    kafka-configs \
    --bootstrap-server "$BROKER" \
    --entity-type topics \
    --entity-name "$TOPIC" \
    --alter \
    --delete-config retention.ms
done

echo "Kafka limpio"
