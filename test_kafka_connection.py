import os
import logging
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
from kafka import KafkaAdminClient
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("KafkaTest")

# Obtener el broker de Kafka desde las variables de entorno o configuración
kafka_broker = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092")  # Cambia a 29092 si usas ese puerto expuesto

def test_kafka_connectivity():
    try:
        # Probar la conexión al broker
        logger.info(f"Probing Kafka at {kafka_broker}...")

        # Intentamos consumir de un tópico ficticio para testear la conectividad
        consumer = KafkaConsumer(bootstrap_servers=kafka_broker)
        consumer.close()
        logger.info("Kafka broker is reachable.")

    except KafkaError as e:
        logger.error(f"Error connecting to Kafka: {e}")
        return False

    return True

def test_advertised_listeners():
    try:
        # Probar la conexión con el cliente de administración de Kafka
        admin_client = KafkaAdminClient(bootstrap_servers=kafka_broker)
        metadata = admin_client.describe_cluster()
        logger.info(f"Kafka Cluster Metadata: {metadata}")

        advertised_listeners = metadata['brokers'][0]['host']  # Asumiendo que se conecta al primer broker
        logger.info(f"Advertised Listener: {advertised_listeners}")

        return advertised_listeners

    except KafkaError as e:
        logger.error(f"Error fetching metadata from Kafka: {e}")
        return None

if __name__ == "__main__":
    logger.info("Starting Kafka connectivity test...")

    if test_kafka_connectivity():
        logger.info("Kafka connection is successful!")
        advertised_listeners = test_advertised_listeners()

        if advertised_listeners:
            logger.info(f"Kafka advertised listeners are properly set: {advertised_listeners}")
        else:
            logger.error("Could not retrieve advertised listeners.")
    else:
        logger.error("Failed to connect to Kafka.")
