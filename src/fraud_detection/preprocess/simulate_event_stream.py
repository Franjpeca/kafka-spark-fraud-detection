import os
import time
import random
import json
import logging
import glob
import pandas as pd
from fraud_detection.config.config_loader import get_config
from pathlib import Path

# Configuración de logging (registrando logs en la carpeta logs/maintenance)
log_dir = Path("logs/maintenance")
log_dir.mkdir(parents=True, exist_ok=True)  # Asegura que la carpeta exista

# Configurar logging con formato personalizado usando "|"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "event_simulator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("event_simulator")

# Cargar configuración desde YAML
cfg = get_config()

# Mapeo tipo -> productor (para cada tipo de transacción)
from payment_producer import produce_payment_message  # Importar productores
from transfer_producer import produce_transfer_message  # Importar otros productores si son necesarios
from cash_out_producer import produce_cash_out_message  # Importar productor de cash_out
from cash_in_producer import produce_cash_in_message  # Importar productor de cash_in
from debit_producer import produce_debit_message  # Importar productor de debit

def simulate_event_stream(parquet_dir: str, delay_range: tuple = (0.1, 1.0)):
    # Leer todos los archivos parquet en la carpeta bronze (o donde guardes)
    parquet_paths = glob.glob(os.path.join(parquet_dir, "*.parquet"))
    for p in parquet_paths:
        logger.info(f"Procesando archivo: {p}")
        df = pd.read_parquet(p)
        for _, row in df.iterrows():
            # Simulamos la llegada de los eventos en intervalos aleatorios
            time.sleep(random.uniform(*delay_range))  # Pausa aleatoria entre eventos
            if row["type"] == "PAYMENT":
                produce_payment_message(row.to_dict())  # Enviar evento a productor de pagos
            elif row["type"] == "TRANSFER":
                produce_transfer_message(row.to_dict())  # Enviar evento a productor de transferencias
            elif row["type"] == "CASH_OUT":
                produce_cash_out_message(row.to_dict())  # Enviar evento a productor de cash_out
            elif row["type"] == "CASH_IN":
                produce_cash_in_message(row.to_dict())  # Enviar evento a productor de cash_in
            elif row["type"] == "DEBIT":
                produce_debit_message(row.to_dict())  # Enviar evento a productor de debit

if __name__ == "__main__":
    bronze_dir = cfg["paths"]["data_bronze"]["root"]
    logger.info(f"Iniciando la simulación de eventos, leyendo desde: {bronze_dir}")
    simulate_event_stream(bronze_dir, delay_range=(0.5, 2.0))  # intervalo entre 0.5 y 2 segundos
    logger.info("Simulación completada.")
