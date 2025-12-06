# PREPROCESADO + ENRIQUECIMIENTO + DIVISIÓN EN PARQUETS POR CHUNK
# Cada parquet representa una "fuente" distinta para Kafka

from pathlib import Path
import pandas as pd
import random
from faker import Faker
import uuid
from datetime import datetime, timedelta
import math

from fraud_detection.config.config_loader import get_config
from fraud_detection.utils.logging_setup import get_logger
from fraud_detection.preprocess.helpers import (
    normalize_columns,
    remove_duplicates,
    generate_timestamp_from_step,
)

logger = get_logger(service_name="maintenance")
fake = Faker()

CHUNK_SIZE = 75000


# ---------------------------------------------------------
# Enriquecimiento por chunk
# ---------------------------------------------------------
def enrich_chunk(df: pd.DataFrame, source_label: str) -> pd.DataFrame:
    n = len(df)
    if n == 0:
        return df

    df["customer_id"] = [str(uuid.uuid4()) for _ in range(n)]
    df["source_system"] = source_label

    if "timestamp" in df.columns:
        df["transaction_datetime"] = df["timestamp"].apply(
            lambda ts: datetime.fromtimestamp(ts) +
                       timedelta(seconds=random.randint(0, 3600))
        )
    else:
        df["transaction_datetime"] = datetime.now()

    df["city"] = [fake.city() for _ in range(n)]
    df["country"] = [fake.country() for _ in range(n)]
    df["currency"] = [random.choice(["EUR", "USD", "GBP"]) for _ in range(n)]
    df["channel"] = [
        random.choice(["ATM", "POS", "ONLINE", "MOBILE", "TRANSFER"])
        for _ in range(n)
    ]

    df["merchant"] = [
        fake.company() if t == "PAYMENT" else None
        for t in df["type"]
    ]

    df["status"] = [
        random.choice(["approved", "declined", "pending"])
        for _ in range(n)
    ]

    return df


# ---------------------------------------------------------
# Procesamiento principal por chunks
# ---------------------------------------------------------
def process_csv_in_chunks(csv_path: Path, bronze_root: Path, chunksize: int = CHUNK_SIZE):

    # -------- CALCULAR FILAS TOTALES SIN CARGAR CSV --------
    logger.info("Contando filas totales del CSV...")
    with open(csv_path, "r", encoding="utf-8") as f:
        total_rows = sum(1 for _ in f) - 1  # Restamos header

    total_chunks = math.ceil(total_rows / chunksize)
    logger.info(f"Total filas: {total_rows} / Total chunks: {total_chunks}")

    bronze_root.mkdir(parents=True, exist_ok=True)

    chunk_id = 0
    processed_rows = 0

    for chunk_df in pd.read_csv(csv_path, chunksize=chunksize):

        logger.info(
            f"Chunk {chunk_id+1}/{total_chunks} leído -- "
            f"{len(chunk_df)} filas -- faltan {total_chunks - (chunk_id+1)} chunks"
        )

        chunk_df = normalize_columns(chunk_df)
        chunk_df = remove_duplicates(chunk_df)
        chunk_df = generate_timestamp_from_step(chunk_df)

        source_label = f"source_{chunk_id}"
        chunk_df = enrich_chunk(chunk_df, source_label)

        tipos = chunk_df["type"].unique()
        for t in tipos:
            sub = chunk_df[chunk_df["type"] == t].copy()

            filename = f"paysim_{t.lower()}_{chunk_id}.parquet"
            out_path = bronze_root / filename

            sub.to_parquet(out_path, index=False)

            logger.info(
                f"Parquet generado: {filename} — {len(sub)} filas — fuente={source_label}"
            )

        processed_rows += len(chunk_df)
        chunk_id += 1

        del chunk_df

    logger.info(
        f"PROCESO COMPLETADO — {processed_rows} filas procesadas en {total_chunks} chunks"
    )


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------
def main():
    logger.info("=== INICIO PREPROCESADO CHUNKED ===")

    cfg = get_config()
    raw_path = Path(cfg["paths"]["data_raw"]["datasets"]["paysim"])
    bronze_root = Path(cfg["paths"]["data_bronze"]["root"])

    process_csv_in_chunks(raw_path, bronze_root)

    logger.info("=== FIN PREPROCESADO CHUNKED ===")


if __name__ == "__main__":
    main()
