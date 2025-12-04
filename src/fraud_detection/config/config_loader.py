import yaml
from pathlib import Path
import functools

@functools.lru_cache(maxsize=1)
def get_config():
    # Ir al directorio raíz del proyecto
    root_path = Path(__file__).resolve().parents[3]
    config_path = root_path / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    return cfg
