#!/bin/bash

BROKER="localhost:29092"

TOPICS=(
  paysim_cash_in
  paysim_cash_out
  paysim_payment
  paysim_transfer
  paysim_debit
)

echo "== Limpiando mensajes Kafka (DEV) =="

for TOPIC in "${TOPICS[@]}"; do
  echo "Limpiando $TOPIC"
  docker exec kafka \
    kafka-configs \
    --bootstrap-server kafka:9092 \
    --entity-type topics \
    --entity-name "$TOPIC" \
    --alter \
    --add-config retention.ms=1000

  sleep 2

  docker exec kafka \
    kafka-configs \
    --bootstrap-server kafka:9092 \
    --entity-type topics \
    --entity-name "$TOPIC" \
    --alter \
    --delete-config retention.ms
done

echo "Kafka limpio"
