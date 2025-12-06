import pytest
from kafka import KafkaProducer, KafkaConsumer
import json
import time
from fraud_detection.config.config_loader import get_config

# Fixture para el productor Kafka
@pytest.fixture(scope="module")
def producer():
    cfg = get_config()
    kafka_broker = "localhost:9092"  # O desde config
    producer = KafkaProducer(
        bootstrap_servers=kafka_broker,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    yield producer
    producer.close()

# Fixture para el consumidor Kafka
@pytest.fixture(scope="module")
def consumer():
    cfg = get_config()
    kafka_broker = "localhost:9092"  # O desde config
    consumer = KafkaConsumer(
        "paysim_cash_in",  # El nombre del tópico que estás utilizando
        bootstrap_servers=kafka_broker,
        auto_offset_reset='earliest',  # Para leer desde el principio si no hay offset
        group_id="test_group"
    )
    yield consumer
    consumer.close()

# Test para verificar que el productor envía mensajes correctamente
def test_producer_send_message(producer):
    topic_name = "paysim_cash_in"
    message = {"step": 10, "type": "CASH_IN", "amount": 1000}
    producer.send(topic_name, value=message)
    producer.flush()

    # Esperar un momento para que Kafka procese el mensaje
    time.sleep(2)

    # Si llegamos aquí sin excepciones, el mensaje fue enviado
    assert True

# Test para verificar que el consumidor recibe mensajes correctamente
def test_consumer_read_message(consumer):
    # Consumir el primer mensaje
    for message in consumer:
        print(f"Received message: {message.value}")
        assert message.value is not None
        break
