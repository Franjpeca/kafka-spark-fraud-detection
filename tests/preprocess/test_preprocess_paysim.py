import pandas as pd

from fraud_detection.preprocess.preprocess_paysim import enrich_chunk
from fraud_detection.preprocess.helpers import (
    normalize_columns,
    remove_duplicates,
    generate_timestamp_from_step,
)


def test_preprocess_basic():
    df = pd.DataFrame({
        "STEP": [1, 2, 2],
        "TYPE": ["CASH_IN", "PAYMENT", "PAYMENT"],
        "AMOUNT": [100, 200, 200],
    })

    # === PROCESAMIENTO EXACTO DEL PIPELINE REAL ===
    df = normalize_columns(df)
    df = remove_duplicates(df)
    df = generate_timestamp_from_step(df)

    # enrich_chunk requiere un source_label
    df_clean = enrich_chunk(df.copy(), source_label="test_source")

    # === VALIDACIONES ===

    # 1. Normalización columnas
    assert "step" in df_clean.columns
    assert "type" in df_clean.columns

    # 2. Duplicados eliminados
    assert len(df_clean) == 2

    # 3. Timestamp generado
    assert "timestamp" in df_clean.columns
    assert df_clean["timestamp"].iloc[0] == 3600

    # 4. Enriquecimiento del chunk
    first = df_clean.iloc[0]

    assert "customer_id" in first
    assert isinstance(first["customer_id"], str)
    assert "source_system" in first
    assert first["source_system"] == "test_source"
    assert "city" in first
    assert "country" in first
    assert "currency" in first
    assert "channel" in first

    # merchant solo aparece para PAYMENT
    if first["type"].upper() == "PAYMENT":
        assert "merchant" in first
