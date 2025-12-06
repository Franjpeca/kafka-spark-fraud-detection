import os
import json
import logging
from kafka import KafkaConsumer
from fraud_detection.config.config_loader import get_config  # Asegúrate de que la ruta de tu configuración es correcta

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("consumer")

# Cargar configuración desde YAML
cfg = get_config()

# Obtener el broker de Kafka desde la configuración, con fallback a localhost:9092
kafka_broker = os.getenv("KAFKA_ADVERTISED_LISTENERS", "localhost:9092")

# Crear consumidor de Kafka
consumer = KafkaConsumer(
    "paysim_cash_in",  # Puedes añadir más topics si es necesario
    bootstrap_servers=kafka_broker,
    group_id="fraud_detection_group",  # Los consumidores se agrupan por ID
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

def consume_messages():
    # Consume mensajes de Kafka
    try:
        for message in consumer:
            logger.info(f"Received message: {message.value}")  # Imprimir el mensaje
    except Exception as e:
        logger.error(f"Error while consuming messages: {e}")
    finally:
        consumer.close()  # Cerrar el consumidor al finalizar

if __name__ == "__main__":
    consume_messages()
