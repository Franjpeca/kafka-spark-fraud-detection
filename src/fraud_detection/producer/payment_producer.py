import os
import json
import logging
from confluent_kafka.avro import AvroProducer
from confluent_kafka.avro import CachedSchemaRegistryClient
from fraud_detection.config.config_loader import get_config
from pathlib import Path
from dotenv import load_dotenv
import random
import time

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("payment_producer")

# Cargar configuración desde YAML
cfg = get_config()

# Obtener el broker de Kafka desde la configuración
kafka_broker = cfg['kafka']['broker']  # Usando configuración de broker de Kafka

# Obtener la URL del Schema Registry desde las variables de entorno
schema_registry_url = os.getenv("SCHEMA_REGISTRY_URL", "http://localhost:8081")  # Valor por defecto si no está en el .env

# Crear cliente de Schema Registry
schema_registry = CachedSchemaRegistryClient(url=schema_registry_url)

# Obtener la ruta del esquema desde la configuración
schema_path = Path(cfg['kafka']['schema_registry']['payment_schema']).resolve()  # Ruta completa

# Cargar el esquema de pago
with open(schema_path, "r") as f:
    schema = json.load(f)

# Crear el productor Avro
producer = AvroProducer(
    {'bootstrap.servers': kafka_broker},
    default_value_schema=schema,
    schema_registry=schema_registry
)

# Mapeo del tópico
topic = "paysim_payment"

def produce_payment_message(message):
    try:
        # Asegurarse de que el mensaje no tiene estructuras no hashables (como diccionarios dentro del mensaje)
        if isinstance(message, dict):
            # Convertir los valores de diccionario a string si son no hashables
            for key, value in message.items():
                if isinstance(value, dict) or isinstance(value, list):  # Si el valor es un diccionario o lista, lo convertimos a string
                    message[key] = str(value)
            
            # Producir mensaje y hacer flush
            producer.produce(topic=topic, value=message)
            producer.flush()  # Asegúrate de que el mensaje se envíe
            logger.info(f"Sent payment message | transaction_id={message['transaction_id']} | amount={message['amount']} | status={message['status']}")
        else:
            logger.error(f"Invalid message format (not a dict): {message}")
    except Exception as e:
        logger.error(f"Error while sending payment message | Error: {e} | Message: {message}")

def listen_for_events():
    # Simular recibir eventos de forma aleatoria
    count = 0
    while count < 10:  # Limitamos a 10 mensajes para pruebas
        logger.info(f"Listening for events... | Event count: {count + 1}")
        
        # Generamos un evento de prueba aleatorio
        event_message = {
            "transaction_id": f"txn_{random.randint(1000, 9999)}",
            "amount": random.randint(10, 500),
            "status": random.choice(["approved", "declined", "pending"]),
            "timestamp": time.time()
        }
        
        # Producimos el mensaje
        logger.info(f"Generated event message | transaction_id={event_message['transaction_id']} | amount={event_message['amount']} | status={event_message['status']}")
        produce_payment_message(event_message)
        
        count += 1
        time.sleep(random.randint(1, 3))  # Esperamos entre 1 y 3 segundos antes de enviar el siguiente

if __name__ == "__main__":
    logger.info(f"Starting producer... | Kafka Broker: {kafka_broker}")
    listen_for_events()
    logger.info("Producer finished.")
