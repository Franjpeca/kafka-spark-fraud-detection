# ===================================================================
#  PREPROCESADO INICIAL DEL DATASET PAYSIM
#  Sistema de deteccion de fraude en tiempo real
# ===================================================================

from pathlib import Path
import pandas as pd

from fraud_detection.config.config_loader import get_config
from fraud_detection.utils.logging_setup import get_logger
from fraud_detection.preprocess.helpers import (
    normalize_columns,
    remove_duplicates,
    generate_timestamp_from_step,
)


# ============================================================
#  Logger del servicio
#  (scripts auxiliares → logs/maintenance/)
# ============================================================
logger = get_logger(service_name="maintenance")


# ============================================================
#  Cargar dataset bruto PaySim
# ============================================================
def load_raw_dataset(raw_path: Path) -> pd.DataFrame:
    logger.info(f"Cargando dataset PaySim desde: {raw_path}")

    if not raw_path.exists():
        logger.error(f"No se encontro el dataset: {raw_path}")
        raise FileNotFoundError(f"No se encontro el dataset PaySim en {raw_path}")

    df = pd.read_csv(raw_path)
    logger.info(f"Dataset cargado correctamente. Filas={len(df)}, Columnas={len(df.columns)}")
    return df


# ============================================================
#  Preprocesado principal
# ============================================================
def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Iniciando preprocesado inicial de PaySim...")

    df = normalize_columns(df)
    df = remove_duplicates(df)
    df = generate_timestamp_from_step(df)

    logger.info("Preprocesado inicial completado con exito.")
    return df


# ============================================================
#  Guardar dataset en capa Bronze
# ============================================================
def save_bronze(df: pd.DataFrame, bronze_path: Path) -> None:
    logger.info(f"Guardando dataset en Bronze: {bronze_path}")

    bronze_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(bronze_path, index=False)

    logger.info("Dataset PaySim guardado correctamente en Bronze.")


# ============================================================
#  Funcion principal del script
# ============================================================
def main():
    logger.info("=== INICIO PREPROCESADO PAYSIM ===")

    config = get_config()

    try:
        # ---------------------------------------------------
        # Acceso a rutas segun config.yaml
        # ---------------------------------------------------
        raw_path = Path(config["paths"]["data_raw"]["datasets"]["paysim"])
        bronze_path = Path(config["paths"]["data_bronze"]["paysim_preprocessed"])

    except KeyError as e:
        logger.error(f"Clave faltante en config.yaml: {e}")
        raise

    df_raw = load_raw_dataset(raw_path)
    df_clean = preprocess(df_raw)
    save_bronze(df_clean, bronze_path)

    logger.info("=== FIN PREPROCESADO PAYSIM ===")


# ============================================================
#  Punto de entrada del script
# ============================================================
if __name__ == "__main__":
    main()
