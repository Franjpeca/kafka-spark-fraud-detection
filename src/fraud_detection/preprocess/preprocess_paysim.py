# PREPROCESADO INICIAL DEL DATASET PAYSIM
# Sistema de detección de fraude en tiempo real

from pathlib import Path
import pandas as pd

from fraud_detection.config.config_loader import get_config
from fraud_detection.utils.logging_setup import get_logger
from fraud_detection.preprocess.helpers import (
    normalize_columns,
    remove_duplicates,
    generate_timestamp_from_step,
)

# Logger del servicio (scripts auxiliares → logs/maintenance/)
logger = get_logger(service_name="maintenance")


# Cargar dataset bruto PaySim
def load_raw_dataset(raw_path: Path) -> pd.DataFrame:
    logger.info(f"Cargando dataset PaySim desde: {raw_path}")

    if not raw_path.exists():
        logger.error(f"No se encontró el dataset: {raw_path}")
        raise FileNotFoundError(f"No se encontró el dataset PaySim en {raw_path}")

    df = pd.read_csv(raw_path)
    logger.info(f"Dataset cargado correctamente. Filas={len(df)}, Columnas={len(df.columns)}")
    return df


# Preprocesado principal
def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Iniciando preprocesado inicial de PaySim...")

    df = normalize_columns(df)
    df = remove_duplicates(df)
    df = generate_timestamp_from_step(df)

    logger.info("Preprocesado inicial completado con éxito.")
    return df


# División en múltiples parquets por tipo de transacción
def save_bronze_by_type(df: pd.DataFrame, bronze_root: Path) -> None:
    logger.info("Generando parquets individuales por tipo de transacción...")

    # Asegurar carpeta bronze
    bronze_root.mkdir(parents=True, exist_ok=True)

    tipos = df["type"].unique()

    for t in tipos:
        subset = df[df["type"] == t].copy()
        filename = f"paysim_{t.lower()}.parquet"
        out_path = bronze_root / filename

        subset.to_parquet(out_path, index=False)
        logger.info(f"Archivo Bronze generado: {out_path} (filas={len(subset)})")

    logger.info("Generación de parquets por tipo completada.")


# Función principal del script
def main():
    logger.info("=== INICIO PREPROCESADO PAYSIM ===")

    config = get_config()

    try:
        raw_path = Path(config["paths"]["data_raw"]["datasets"]["paysim"])
        bronze_root = Path(config["paths"]["data_bronze"]["root"])
    except KeyError as e:
        logger.error(f"Clave faltante en config.yaml: {e}")
        raise

    df_raw = load_raw_dataset(raw_path)
    df_clean = preprocess(df_raw)

    # Guardar múltiples parquets por tipo
    save_bronze_by_type(df_clean, bronze_root)

    logger.info("=== FIN PREPROCESADO PAYSIM ===")


# Punto de entrada del script
if __name__ == "__main__":
    main()
