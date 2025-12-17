#!/bin/bash
set -e

echo "== Limpieza entorno DEV =="

echo "-> Limpiando Kafka"
bash "$(dirname "$0")/reset_kafka.sh"

echo "-> Limpiando PostgreSQL"
bash "$(dirname "$0")/reset_postgres.sh"

echo "Entorno limpio"
