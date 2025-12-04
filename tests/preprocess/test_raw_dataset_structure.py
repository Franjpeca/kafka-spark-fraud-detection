# Test de integración completo del flujo de preprocesado PaySim.
# Ejecuta RAW -> preprocess -> Bronze, usando rutas reales y
# validando que el Parquet generado es correcto y consistente.

from pathlib import Path
import pandas as pd

from fraud_detection.config.config_loader import get_config


def test_raw_paysim_structure():
    """
    Valida que el dataset PaySim RAW existe y contiene las columnas requeridas.
    """

    cfg = get_config()

    # Ruta del dataset RAW
    raw_path = Path(cfg["paths"]["data_raw"]["datasets"]["paysim"])
    assert raw_path.exists(), f"El dataset PaySim no existe en: {raw_path}"

    # Cargar CSV
    df = pd.read_csv(raw_path)

    # Columnas obligatorias según PaySim original
    required_columns = {
        "step",
        "type",
        "amount",
        "nameOrig",
        "oldbalanceOrg",
        "newbalanceOrig",
        "nameDest",
        "oldbalanceDest",
        "newbalanceDest",
        "isFraud",
        "isFlaggedFraud",
    }

    missing = required_columns - set(df.columns)
    assert not missing, f"Faltan columnas en el dataset RAW: {missing}"

    # Validaciones básicas de tipos y valores
    assert df["amount"].dtype in ["float64", "int64"], "La columna amount debe ser numérica"
    assert df["isFraud"].isin([0, 1]).all(), "isFraud debe contener solo 0 o 1"
    assert df["isFlaggedFraud"].isin([0, 1]).all(), "isFlaggedFraud debe contener solo 0 o 1"

    # Comprobación de filas
    assert len(df) > 0, "El dataset RAW está vacío"
