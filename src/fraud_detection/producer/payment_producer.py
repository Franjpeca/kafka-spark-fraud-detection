import os
import json
import logging
import time
from pathlib import Path
from dotenv import load_dotenv

from confluent_kafka.avro import AvroProducer, CachedSchemaRegistryClient
from avro.schema import parse as avro_parse

from fraud_detection.config.config_loader import get_config

# ------------------------------------------------------------
# Cargar variables de entorno
# ------------------------------------------------------------
load_dotenv()

# ------------------------------------------------------------
# Configurar logging estilo profesional
# ------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | payment_producer | %(levelname)s | %(message)s"
)
logger = logging.getLogger("payment_producer")

# ------------------------------------------------------------
# Cargar config YAML
# ------------------------------------------------------------
cfg = get_config()
kafka_broker = cfg["kafka"]["broker"]
schema_registry_url = os.getenv("SCHEMA_REGISTRY_URL", "http://localhost:8081")

# ------------------------------------------------------------
# Cargar esquema AVRO parseado
# ------------------------------------------------------------
schema_path = Path(cfg["kafka"]["schema_registry"]["payment_schema"]).resolve()

with open(schema_path, "r") as f:
    raw_schema = f.read()

value_schema = avro_parse(raw_schema)

# ------------------------------------------------------------
# Crear cliente de Schema Registry
# ------------------------------------------------------------
schema_registry = CachedSchemaRegistryClient({
    "url": schema_registry_url
})

# ------------------------------------------------------------
# Crear AvroProducer
# ------------------------------------------------------------
producer = AvroProducer(
    {
        "bootstrap.servers": kafka_broker,
        "on_delivery": lambda err, msg: logger.error(f"Delivery error: {err}") if err else None
    },
    default_value_schema=value_schema,
    schema_registry=schema_registry
)

topic = "paysim_payment"


# ------------------------------------------------------------
# Normalización segura de mensaje según AVRO
# ------------------------------------------------------------
def _clean_value(value, field_type):
    """
    AVRO no acepta dict, list, NaN, ni tipos raros.
    Esta función convierte todo a tipos válidos.
    """
    if value is None:
        return None

    # En caso de union types como ["null","string"]
    if isinstance(field_type, list):
        field_type = [t for t in field_type if t != "null"][0]

    if field_type == "string":
        return str(value)
    if field_type == "int":
        return int(value)
    if field_type == "long":
        return int(value)
    if field_type == "double":
        return float(value)
    if field_type == "boolean":
        return bool(value)

    return value


# ------------------------------------------------------------
# Productor principal: genera mensajes AVRO válidos
# ------------------------------------------------------------
def produce_payment_message(message: dict):
    try:
        clean_message = {}

        for field in value_schema.fields:
            name = field.name
            field_type = field.type

            if name in message:
                clean_message[name] = _clean_value(message[name], field_type)
            else:
                clean_message[name] = getattr(field, "default", None)

        logger.info(
            f"Producing | txn={clean_message.get('transaction_id')} | "
            f"amount={clean_message.get('amount')} | type={clean_message.get('type')}"
        )

        producer.produce(topic=topic, value=clean_message)
        producer.flush()

        logger.info(
            f"Sent OK | txn={clean_message.get('transaction_id')} | "
            f"amount={clean_message.get('amount')} | type={clean_message.get('type')}"
        )

    except Exception as e:
        logger.error(f"Error sending message | {e} | msg={message}")


# ------------------------------------------------------------
# (Opcional) Generador sintético para debug
# ------------------------------------------------------------
def listen_for_events():
    logger.info(f"Starting PAYMENT producer | broker={kafka_broker}")

    for i in range(10):
        event_message = {
            "step": None,
            "type": "PAYMENT",
            "amount": 50.0 + i,
            "nameorig": "C12345",
            "namedest": None,
            "isfraud": 0,
            "isflaggedfraud": 0,
            "timestamp": int(time.time()),
            "customer_id": "AUTO",
            "source_system": "test_simulator",
            "transaction_datetime": str(time.time()),
            "city": "Madrid",
            "country": "Spain",
            "currency": "EUR",
            "channel": "ONLINE",
            "merchant": "TestCorp",
            "status": "approved",
        }

        logger.info(f"Generated mock event | txn=test_event_{i}")

        produce_payment_message(event_message)
        time.sleep(1)

    logger.info("Producer finished.")


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
if __name__ == "__main__":
    listen_for_events()
