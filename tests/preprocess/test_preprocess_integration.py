# Test de integración completo del flujo de preprocesado PaySim.
# Ejecuta RAW → preprocess → Bronze (parquets por tipo),
# usando rutas reales y validando que los Parquets generados son correctos y consistentes.

import pandas as pd
from pathlib import Path

from fraud_detection.config.config_loader import get_config
from fraud_detection.preprocess.preprocess_paysim import (
    load_raw_dataset,
    preprocess,
    save_bronze_by_type,
)


def test_preprocess_end_to_end(tmp_path):
    """
    Test de integración: 
    Ejecuta el flujo completo de preprocesado:
    RAW → preprocess() → Bronze (parquets por tipo).
    """

    cfg = get_config()

    # Rutas reales
    raw_path = Path(cfg["paths"]["data_raw"]["datasets"]["paysim"])
    assert raw_path.exists(), "El dataset PaySim no existe en data/raw/datasets/"

    # Ruta temporal para almacenar los parquets generados en Bronze
    bronze_temp = tmp_path / "bronze"
    
    # 1. Cargar RAW
    df_raw = load_raw_dataset(raw_path)
    assert len(df_raw) > 0, "El dataset RAW está vacío"

    # 2. Preprocesar
    df_clean = preprocess(df_raw)
    assert "timestamp" in df_clean.columns, "La columna timestamp no fue generada"
    assert len(df_clean) > 0, "El preprocesado generó un dataframe vacío"

    # 3. Guardar los parquets por tipo
    save_bronze_by_type(df_clean, bronze_temp)

    # Verificar que se han generado los parquets por tipo
    tipos = df_clean["type"].unique()
    assert len(tipos) > 0, "No se encontraron tipos de transacción en el dataframe"

    for t in tipos:
        parquet_file = bronze_temp / f"paysim_{t.lower()}.parquet"
        assert parquet_file.exists(), f"El archivo {parquet_file} no fue creado"

        # Validar que el parquet generado contiene datos
        df_check = pd.read_parquet(parquet_file)
        assert len(df_check) > 0, f"El parquet {parquet_file} está vacío"
        assert "timestamp" in df_check.columns, f"El parquet {parquet_file} no contiene la columna timestamp"
        
        # Validar que el parquet contiene solo un tipo de transacción
        assert df_check["type"].iloc[0] == t, f"El parquet {parquet_file} tiene un tipo incorrecto. Esperado {t}."

    # Asegurarse de que todos los archivos esperados existen
    for t in tipos:
        expected_file = bronze_temp / f"paysim_{t.lower()}.parquet"
        assert expected_file.exists(), f"El archivo esperado {expected_file} no fue creado."

    print("Test de integración completado con éxito.")
