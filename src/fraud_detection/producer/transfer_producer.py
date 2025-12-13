import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv
import uuid  # Asegúrate de importar el módulo uuid

from confluent_kafka.avro import AvroProducer, CachedSchemaRegistryClient
from avro.schema import parse as avro_parse

from fraud_detection.config.config_loader import get_config

# ============================================================
# Cargar variables de entorno
# ============================================================
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | transfer_producer | %(levelname)s | %(message)s"
)
logger = logging.getLogger("transfer_producer")

# ============================================================
# Cargar configuración general
# ============================================================
cfg = get_config()
kafka_broker = cfg["kafka"]["broker"]
schema_registry_url = os.getenv("SCHEMA_REGISTRY_URL", "http://localhost:8081")

# ============================================================
# Cargar esquema AVRO
# ============================================================
schema_path = Path(cfg["kafka"]["schema_registry"]["transfer_schema"]).resolve()
with open(schema_path, "r") as f:
    raw_schema = f.read()

value_schema = avro_parse(raw_schema)

schema_registry = CachedSchemaRegistryClient({"url": schema_registry_url})

# ============================================================
# Crear AvroProducer
# ============================================================
producer = AvroProducer(
    {
        "bootstrap.servers": kafka_broker,
        "on_delivery": lambda err, msg: logger.error(f"Delivery error: {err}") if err else None
    },
    default_value_schema=value_schema,
    schema_registry=schema_registry
)

topic = "paysim_transfer"

# ============================================================
# Normalización segura
# ============================================================
def _clean_value(value, field_type):
    if value is None:
        return None

    if isinstance(field_type, list):
        field_type = [t for t in field_type if t != "null"][0]

    if field_type == "string":
        return str(value)
    if field_type == "int":
        return int(value)
    if field_type == "long":
        # Asegúrate de que el valor sea un entero largo
        return int(value)  # Si ya es un número entero, no es necesario hacer nada
    if field_type == "double":
        return float(value)
    if field_type == "boolean":
        return bool(value)

    return value

# ============================================================
# FUNCIÓN FINAL: PRODUCIR MENSAJE AL RECIBIRLO DEL SIMULADOR
# ============================================================
def produce_transfer_message(message: dict):
    try:
        clean_message = {}

        # Limpiar y formatear los datos según el esquema AVRO
        for field in value_schema.fields:
            name = field.name
            field_type = field.type

            if name in message:
                clean_message[name] = _clean_value(message[name], field_type)
            else:
                clean_message[name] = getattr(field, "default", None)

        # Verificar que `transaction_id` esté presente
        if 'transaction_id' not in clean_message or clean_message['transaction_id'] is None:
            logger.warning(f"Missing or None transaction_id: {message}")
            # Aquí generamos un ID único para cada transacción si falta
            clean_message['transaction_id'] = str(uuid.uuid4())

        # Asegurémonos de tener un `transaction_id` válido
        transaction_id = clean_message.get('transaction_id', 'UNKNOWN')

        logger.info(
            f"Producing | txn={transaction_id} | amount={clean_message.get('amount')} "
            f"| type={clean_message.get('type')}"
        )

        # Producir el mensaje a Kafka
        producer.produce(topic=topic, value=clean_message)
        producer.flush()

        logger.info(f"Sent OK | txn={transaction_id}")
        return True

    except Exception as e:
        logger.error(f"Error sending message | {e} | msg={message}")
        return False
