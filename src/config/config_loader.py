import yaml
from pathlib import Path
import functools

@functools.lru_cache(maxsize=1)
def get_config():
    root_path = Path(__file__).resolve().parents[2]
    config_path = root_path / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    return cfg