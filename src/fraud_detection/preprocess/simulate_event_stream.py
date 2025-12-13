import os
import time
import random
import logging
import glob
import threading
import pandas as pd
import uuid

from pathlib import Path
from fraud_detection.config.config_loader import get_config

# Importar productores específicos
from fraud_detection.producer.payment_producer import produce_payment_message
from fraud_detection.producer.cash_in_producer import produce_cash_in_message
from fraud_detection.producer.cash_out_producer import produce_cash_out_message
from fraud_detection.producer.transfer_producer import produce_transfer_message
from fraud_detection.producer.debit_producer import produce_debit_message

# === Configuración de logging profesional ===
log_dir = Path("logs/maintenance")
log_dir.mkdir(parents=True, exist_ok=True)

LOG_FORMAT = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"

# --- Logger principal para el simulador ---
simulator_logger = logging.getLogger("simulator")
simulator_logger.setLevel(logging.INFO)
sim_handler = logging.StreamHandler()
sim_handler.setFormatter(logging.Formatter(LOG_FORMAT))
simulator_logger.addHandler(sim_handler)
simulator_logger.propagate = False

# --- También opcional: FileHandler rotativo sólo para simulador ---
from logging.handlers import RotatingFileHandler
file_handler = RotatingFileHandler("logs/simulator.log", maxBytes=10*1024*1024, backupCount=5)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
simulator_logger.addHandler(file_handler)

cfg = get_config()

# ===========================
# Función para obtener un logger específico para cada productor
# ===========================
def get_logger_for_producer(producer_name: str):
    """
    Devuelve un logger con el nombre del productor específico.
    """
    logger = logging.getLogger(producer_name)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(handler)

    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger

# ===========================
# Definición de campos permitidos por AVRO
# ===========================
ALLOWED_FIELDS = {
    "step", "type", "amount", "nameorig", "namedest", "isfraud", "isflaggedfraud",
    "timestamp", "customer_id", "source_system", "transaction_datetime",
    "city", "country", "currency", "channel", "merchant", "status"
}

# ===========================
# Configuración de delays aleatorios por tipo de transacción
# ===========================
delay_config = {
    "PAYMENT": (0.2, 1.0),
    "CASH_IN": (0.5, 2.0),
    "CASH_OUT": (0.5, 2.5),
    "TRANSFER": (0.1, 0.8),
    "DEBIT": (0.5, 1.5),
}

# ===========================
# Función para limpiar datos antes de enviarlos a Kafka
# ===========================
def clean_row_for_avro(row_dict: dict) -> dict:
    clean = {}
    for k, v in row_dict.items():
        if k not in ALLOWED_FIELDS:
            continue
        if pd.isna(v):
            clean[k] = None
        elif isinstance(v, pd.Timestamp):
            clean[k] = v.isoformat()
        else:
            clean[k] = v

    if 'transaction_id' not in clean or clean['transaction_id'] is None:
        clean['transaction_id'] = str(uuid.uuid4())
    return clean

# ===========================
# Función para obtener el delay aleatorio
# ===========================
def get_random_delay(tx_type: str):
    if tx_type in delay_config:
        low, high = delay_config[tx_type]
        return random.uniform(low, high)
    return random.uniform(0.1, 1.0)

# ===========================
# Worker que procesa los archivos parquet y produce eventos con delay aleatorio
# ===========================
def parquet_worker(parquet_paths, event_type, producer_fn, logger):
    logger.info(f"[{event_type}] Worker iniciado. {len(parquet_paths)} archivos.")

    for path in parquet_paths:
        df = pd.read_parquet(path)
        logger.info(f"[{event_type}] Leyendo {path} ({len(df)} filas)")
        for _, row in df.iterrows():
            time.sleep(get_random_delay(event_type))
            event = clean_row_for_avro(row.to_dict())
            producer_fn(event)

    logger.info(f"[{event_type}] Worker completado.")

# ===========================
# Función principal que ejecuta la simulación
# ===========================
def run_simulation(bronze_dir: str):
    simulator_logger.info("=== Iniciando simulación multithread con delays aleatorios ===")
    workers = []

    files_map = {
        "PAYMENT": ("paysim_payment_*.parquet", produce_payment_message),
        "CASH_IN": ("paysim_cash_in_*.parquet", produce_cash_in_message),
        "CASH_OUT": ("paysim_cash_out_*.parquet", produce_cash_out_message),
        "TRANSFER": ("paysim_transfer_*.parquet", produce_transfer_message),
        "DEBIT": ("paysim_debit_*.parquet", produce_debit_message),
    }

    for event_type, (pattern, producer_fn) in files_map.items():
        paths = glob.glob(os.path.join(bronze_dir, pattern))
        proc_logger = get_logger_for_producer(f"{event_type.lower()}_producer")

        if not paths:
            simulator_logger.info(f"[{event_type}] No se encontraron archivos para procesar.")
            continue

        simulator_logger.info(f"[{event_type}] Archivos detectados ({len(paths)}), lanzando worker.")

        thread = threading.Thread(
            target=parquet_worker,
            args=(paths, event_type, producer_fn, proc_logger),
            daemon=True
        )
        workers.append(thread)

    for t in workers:
        t.start()
    for t in workers:
        t.join()

    simulator_logger.info("=== Simulación COMPLETADA ===")

if __name__ == "__main__":
    bronze_dir = cfg["paths"]["data_bronze"]["root"]
    run_simulation(bronze_dir)
