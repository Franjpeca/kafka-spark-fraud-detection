from fraud_detection.utils.logging_setup import get_logger
import pandas as pd

logger = get_logger(service_name="maintenance")


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Normalizando nombres de columnas...")
    df = df.copy()
    df.columns = [col.strip().lower() for col in df.columns]
    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    df_clean = df.drop_duplicates()
    removed = before - len(df_clean)
    logger.info(f"Duplicados eliminados: {removed}")
    return df_clean


def generate_timestamp_from_step(df: pd.DataFrame) -> pd.DataFrame:
    if "step" not in df.columns:
        logger.warning("Columna 'step' no encontrada. Se omite generacion de timestamp.")
        return df

    df = df.copy()
    df["timestamp"] = df["step"] * 3600  # 1 step = 1 hora
    logger.info("Timestamp generado a partir de columna 'step'.")
    return df
