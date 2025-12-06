from pathlib import Path
import pandas as pd
import tempfile
from fraud_detection.preprocess.preprocess_paysim import process_csv_in_chunks


def test_preprocess_chunked_small(tmp_path):

    # Crear CSV pequeño sintético
    small_df = pd.DataFrame({
        "step": [1, 2, 3, 4],
        "type": ["CASH_IN", "PAYMENT", "CASH_OUT", "PAYMENT"],
        "amount": [100, 50, 20, 80],
    })

    csv_path = tmp_path / "small_paysim.csv"
    small_df.to_csv(csv_path, index=False)

    bronze_root = tmp_path / "bronze"

    # Procesar en chunks pequeños para test (chunk = 2)
    process_csv_in_chunks(csv_path, bronze_root, chunksize=2)

    # Verificar que se generaron parquet(s)
    parquet_files = list(bronze_root.glob("*.parquet"))
    assert len(parquet_files) > 0, "No se generaron parquets en el test"

    # Validar contenido
    df_sample = pd.read_parquet(parquet_files[0])
    assert "timestamp" in df_sample.columns
    assert "customer_id" in df_sample.columns
    assert "source_system" in df_sample.columns
    assert len(df_sample) > 0
