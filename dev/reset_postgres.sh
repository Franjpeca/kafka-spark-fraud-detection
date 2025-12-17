#!/bin/bash
set -e

echo "-> Borrando tablas PostgreSQL (DEV)"

docker exec -i postgresql psql \
  -U pguser \
  -d paysim_historic_db \
  -c "
    TRUNCATE TABLE
      cash_in_transaction,
      cash_out_transaction,
      payment_transaction,
      transfer_transaction,
      debit_transaction
    RESTART IDENTITY CASCADE;
  "

echo "PostgreSQL limpio"
    