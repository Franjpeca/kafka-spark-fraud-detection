import pandas as pd
from fraud_detection.preprocess.preprocess_paysim import preprocess


def test_preprocess_basic():
    df = pd.DataFrame({
        "STEP": [1, 2, 2],
        "AMOUNT": [100, 200, 200]
    })

    df_clean = preprocess(df)

    assert "step" in df_clean.columns
    assert "timestamp" in df_clean.columns
    assert len(df_clean) == 2  # un duplicado eliminado
    assert df_clean["timestamp"].iloc[0] == 3600
