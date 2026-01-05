import pandas as pd
from pathlib import Path


def load_paysim(path: str) -> pd.DataFrame:
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Dataset no encontrado: {path}")

    if path.suffix == ".csv":
        return pd.read_csv(path)
    elif path.suffix == ".parquet":
        return pd.read_parquet(path)

    raise ValueError(f"Formato no soportado: {path.suffix}")
