# dataset_paysim.md

## 1. Dataset original: PaySim1.csv

El dataset PaySim es una simulación de transacciones financieras basada en patrones reales. 
Se utiliza ampliamente para experimentos de detección de fraude y benchmarking.

A continuación se documentan las columnas originales del archivo `PaySim1.csv`:

---

## 1.1 Columnas originales y significado

| Columna             | Descripción                                                                 | Tipo     | Nota técnica |
|---------------------|-----------------------------------------------------------------------------|----------|--------------|
| step                | Número de horas desde el inicio de la simulación (0–743).                   | int      | No es fecha real. Se convertirá a timestamp. |
| type                | Tipo de transacción (PAYMENT, TRANSFER, CASH_OUT, CASH_IN, DEBIT).         | string   | Categoría operativa. |
| amount              | Monto de la transacción.                                                    | float    | En una única moneda genérica. |
| nameOrig            | Identificador del usuario que origina la transacción.                      | string   | IDs sintéticos tipo C123xxxx o Mxxxxxx. |
| oldbalanceOrg       | Saldo de origen antes de la transacción.                                   | float    | Puede tener inconsistencias típicas de PaySim. |
| newbalanceOrig      | Saldo de origen después de la transacción.                                 | float    | Puede no cuadrar por ser simulación. |
| nameDest            | Identificador del receptor de la transacción.                              | string   | Clientes (Cxxxxx) o comercios (Mxxxxx). |
| oldbalanceDest      | Saldo del receptor antes de la transacción.                                | float    | A menudo 0 o vacío. |
| newbalanceDest      | Saldo del receptor después de la transacción.                              | float    | A menudo 0 o vacío. |
| isFraud             | 1 si la transacción es fraudulenta.                                        | int      | Etiqueta sintética. |
| isFlaggedFraud      | 1 si un sistema previo marcó la transacción como sospechosa.               | int      | Otra etiqueta sintética. |

---

## 2. Columnas que se eliminarán en el preprocesamiento

| Columna           | Razón de eliminación                                                           |
|-------------------|--------------------------------------------------------------------------------|
| oldbalanceOrg     | No aporta valor a eventos transaccionales en streaming.                       |
| newbalanceOrig     | No se utiliza para reglas ni features del sistema en tiempo real.            |
| oldbalanceDest     | Campo incompleto y poco realista (casi siempre 0).                           |
| newbalanceDest     | Campo incompleto y no representa balances reales.                            |
| isFlaggedFraud     | No se usa en el pipeline inicial (reglas propias + modelo futuro).           |

Estas columnas vienen de la simulación PaySim y no existen en sistemas reales exactamente así, además de ser inconsistentes. Para un pipeline Kafka → Spark son ruido.

---

## 3. Columnas que se renombrarán

| Original     | Nuevo nombre      | Motivo |
|--------------|-------------------|--------|
| nameOrig     | origin_id         | Estándar más descriptivo. |
| nameDest     | destination_id    | Claridad en eventos. |
| step         | step              | Se mantiene pero se convertirá a timestamp. |
| isFraud      | is_fraud          | Estilo snake_case. |

---

## 4. Columnas nuevas que se añadirán (enriquecimiento)

En el flujo de procesamiento, se agregan varias columnas adicionales. Estas columnas se añaden **a todas las transacciones**, excepto la columna `merchant`, que solo se genera para transacciones de tipo **`PAYMENT`**.

| Nueva columna       | Descripción                                                                 | Motivo técnico |
|---------------------|-----------------------------------------------------------------------------|----------------|
| `transaction_id`     | UUID único para cada evento.                                                | Necesario en Kafka/Spark. |
| `timestamp`          | Fecha/hora real convertida desde `step`, con un retraso aleatorio de hasta una hora. | Streaming real. |
| `event_time_ms`      | Timestamp en milisegundos para Kafka.                                       | Ordenación y particiones. |
| `country`            | País del origen o destino.                                                  | Reglas por ubicación. |
| `currency`           | Moneda usada.                                                               | Normalización y ML futuro. |
| `channel`            | Canal de la transacción (web, mobile, atm).                                 | Reglas de fraude. |
| `device_id`          | Identificador sintético del dispositivo.                                    | Reglas + features. |
| `merchant`           | Nombre de la empresa (solo para transacciones de tipo `PAYMENT`).           | Reglas de fraude. |

**Nota importante:**  
- Todas las columnas son generadas de manera aleatoria **para todos los tipos de transacción** (excepto `merchant`).
- La columna **`merchant`** se asigna solo a las transacciones de tipo **`PAYMENT`**. Para las demás transacciones (como `TRANSFER`, `CASH_OUT`, etc.), esta columna no se llena.


---

## 5. Esquema final del evento (para Kafka)

| Columna            | Origen        |
|--------------------|---------------|
| transaction_id     | Generada      |
| timestamp          | Derivada de step |
| event_time_ms      | Generada      |
| type               | PaySim        |
| amount             | PaySim        |
| origin_id          | PaySim (nameOrig renombrado) |
| destination_id     | PaySim (nameDest renombrado) |
| country            | Generada      |
| currency           | Generada      |
| channel            | Generada      |
| device_id          | Generada      |
| is_fraud               | PaySim (isFraud renombrado) |

---

## 6. Resumen del flujo de transformación

1. Cargar `PaySim1.csv` desde `data/raw/original/`.
2. Renombrar columnas para adecuarlo al modelo lógico del sistema.
3. Eliminar columnas innecesarias para tiempo real.
4. Convertir `step` en timestamp real.
5. Añadir columnas simuladas (country, currency, channel, device_id).
6. Generar `transaction_id` único.
7. Guardar resultado en `data/bronze/paysim_prepared.parquet`.

Este dataset en Bronze será el que consuma el generador de eventos Kafka.
