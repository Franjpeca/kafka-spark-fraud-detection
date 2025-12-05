import os
import json
import logging
import pandas as pd
from kafka import KafkaProducer
from fraud_detection.config.config_loader import get_config  # Asegúrate de que la ruta de tu configuración es correcta

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("producer")

# Cargar configuración desde YAML
cfg = get_config()

# Obtener el broker de Kafka desde la configuración, con fallback a localhost:9092
kafka_broker = os.getenv("KAFKA_ADVERTISED_LISTENERS", "localhost:9092")

# Crear productor de Kafka
producer = KafkaProducer(
    bootstrap_servers=kafka_broker,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Rutas de los archivos Parquet
parquet_files = {
    "cash_in": cfg["paths"]["data_bronze"]["paysim_cash_in_parquet"],
    "cash_out": cfg["paths"]["data_bronze"]["paysim_cash_out_parquet"],
    "debit": cfg["paths"]["data_bronze"]["paysim_debit_parquet"],
    "payment": cfg["paths"]["data_bronze"]["paysim_payment_parquet"],
    "transfer": cfg["paths"]["data_bronze"]["paysim_transfer_parquet"]
}

def send_to_kafka(parquet_file, topic):
    # Leer el archivo Parquet
    try:
        logger.info(f"Reading Parquet file: {parquet_file}")
        df = pd.read_parquet(parquet_file)

        # Enviar cada fila como mensaje a Kafka
        for index, row in df.iterrows():
            message = row.to_dict()  # Convertir cada fila en un diccionario
            producer.send(topic, value=message)
            logger.info(f"Sent message to {topic}: {message}")
    except Exception as e:
        logger.error(f"Error reading file {parquet_file}: {e}")

def main():
    # Enviar a los tópicos correspondientes
    for transaction_type, parquet_file in parquet_files.items():
        topic = f"paysim_{transaction_type}"  # Ejemplo: paysim_cash_in
        logger.info(f"Sending data to Kafka topic: {topic}")
        send_to_kafka(parquet_file, topic)

    # Cerrar productor
    producer.flush()
    producer.close()
    logger.info("Kafka Producer finished sending messages.")

if __name__ == "__main__":
    main()
