import os
import time
import threading
import logging

from dotenv import load_dotenv
load_dotenv()

from confluent_kafka import Consumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import SerializationContext, MessageField

from prometheus_client import start_http_server, Counter, Histogram

from fraud_detection.config.config_loader import get_config


cfg = get_config()

kafka_cfg = cfg["kafka"]
metrics_cfg = cfg["metrics"]
paths_cfg = cfg["paths"]
logging_cfg = cfg["logging"]

service_name = metrics_cfg.get("service_name", "metrics_service")

broker = kafka_cfg["broker"]
topics = kafka_cfg["topics"]

consumer_cfg = metrics_cfg["consumer"]
group_id = consumer_cfg["group_id"]
auto_offset_reset = consumer_cfg.get("auto_offset_reset", "latest")
enable_auto_commit = consumer_cfg.get("enable_auto_commit", True)

metrics_port = metrics_cfg["server"]["port"]

duplicates_cfg = metrics_cfg["duplicates"]
duplicates_enabled = duplicates_cfg.get("enabled", True)
duplicate_ttl_seconds = duplicates_cfg.get("ttl_seconds", 300)

schema_registry_url = os.getenv("SCHEMA_REGISTRY_URL", "http://schema-registry:8081")


logs_root = paths_cfg["logs"]["root"]
logs_dir = os.path.join(logs_root, "services")
os.makedirs(logs_dir, exist_ok=True)

log_file = os.path.join(logs_dir, "metrics_service.log")

logging.basicConfig(
    level=logging_cfg.get("level", "INFO"),
    format="%(asctime)s | metrics_service | %(levelname)s | %(message)s",
    handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
)

logger = logging.getLogger(service_name)


events_total = Counter(
    "events_total",
    "Total number of events consumed",
)

events_by_topic = Counter(
    "events_by_topic_total",
    "Total number of events consumed per topic",
    ["topic"],
)

duplicate_ids_total = Counter(
    "duplicate_ids_total",
    "Total number of duplicated transaction_id detected",
)

consumer_errors_total = Counter(
    "consumer_errors_total",
    "Total number of Kafka consumer/deserialization errors",
)

event_latency_seconds = Histogram(
    "event_latency_seconds",
    "Latency between event timestamp (ms) and consumption time",
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10, 30),
)


seen_ids = {}
seen_ids_lock = threading.Lock()


schema_registry_client = SchemaRegistryClient({"url": schema_registry_url})
avro_deserializer = AvroDeserializer(schema_registry_client)


def create_consumer():
    return Consumer(
        {
            "bootstrap.servers": broker,
            "group.id": group_id,
            "auto.offset.reset": auto_offset_reset,
            "enable.auto.commit": enable_auto_commit,
        }
    )


def cleanup_seen_ids():
    if not duplicates_enabled:
        return

    while True:
        now = time.time()
        with seen_ids_lock:
            expired = [
                txn_id
                for txn_id, ts in seen_ids.items()
                if now - ts > duplicate_ttl_seconds
            ]
            for txn_id in expired:
                del seen_ids[txn_id]
        time.sleep(30)


def deserialize_record(msg):
    return avro_deserializer(
        msg.value(),
        SerializationContext(msg.topic(), MessageField.VALUE),
    )


def consume_loop():
    consumer = create_consumer()
    consumer.subscribe(topics)

    logger.info("Metrics consumer started")
    logger.info("Schema Registry: %s", schema_registry_url)
    logger.info("Consumer group: %s", group_id)
    logger.info("Subscribed topics: %s", ", ".join(topics))

    try:
        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                continue

            if msg.error():
                consumer_errors_total.inc()
                logger.error("Kafka consumer error: %s", msg.error())
                continue

            topic = msg.topic()

            events_total.inc()
            events_by_topic.labels(topic=topic).inc()

            try:
                record = deserialize_record(msg)
            except Exception as exc:
                consumer_errors_total.inc()
                logger.error("Avro deserialization error: %s", exc)
                continue

            txn_id = None
            try:
                txn_id = record.get("transaction_id")
            except Exception:
                txn_id = None

            if duplicates_enabled and txn_id:
                with seen_ids_lock:
                    if txn_id in seen_ids:
                        duplicate_ids_total.inc()
                    else:
                        seen_ids[txn_id] = time.time()

            try:
                ts_ms = record.get("timestamp")
            except Exception:
                ts_ms = None

            if ts_ms is not None:
                now_ms = int(time.time() * 1000)
                latency_sec = (now_ms - int(ts_ms)) / 1000.0
                if latency_sec >= 0:
                    event_latency_seconds.observe(latency_sec)

    finally:
        consumer.close()


if __name__ == "__main__":
    logger.info("Starting metrics HTTP server on port %s", metrics_port)
    start_http_server(metrics_port)

    if duplicates_enabled:
        threading.Thread(target=cleanup_seen_ids, daemon=True).start()

    consume_loop()
