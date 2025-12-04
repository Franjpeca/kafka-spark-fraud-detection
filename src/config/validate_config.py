# Valida que config.yaml contiene todas las claves necesarias y que las rutas y ficheros declarados existen.
# Evita errores antes de ejecutar scripts, Spark, Kafka o cualquier componente del proyecto.

from pathlib import Path
import sys
from typing import List, Dict, Any

from config.config_loader import get_config



REQUIRED_PATH_KEYS = [
    ("paths",),
    ("paths", "data_raw"),
    ("paths", "data_raw", "root"),
    ("paths", "data_raw", "datasets"),
    ("paths", "data_raw", "datasets", "root"),
    ("paths", "data_raw", "datasets", "paysim"),
    ("paths", "data_bronze"),
    ("paths", "data_bronze", "root"),
    ("paths", "data_silver"),
    ("paths", "data_silver", "root"),
    ("paths", "data_gold"),
    ("paths", "data_gold", "root"),
]


def get_nested(cfg: Dict[str, Any], path: tuple) -> Any:
    cur = cfg
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            raise KeyError("Missing config key: " + " -> ".join(path))
        cur = cur[key]
    return cur


def validate_required_keys(cfg: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    for key_path in REQUIRED_PATH_KEYS:
        try:
            get_nested(cfg, key_path)
        except KeyError as exc:
            errors.append(str(exc))
    return errors


def validate_directories_and_files(cfg: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    try:
        data_raw_root = Path(get_nested(cfg, ("paths", "data_raw", "root")))
        datasets_root = Path(get_nested(cfg, ("paths", "data_raw", "datasets", "root")))
        paysim_file = Path(get_nested(cfg, ("paths", "data_raw", "datasets", "paysim")))
        bronze_root = Path(get_nested(cfg, ("paths", "data_bronze", "root")))
        silver_root = Path(get_nested(cfg, ("paths", "data_silver", "root")))
        gold_root = Path(get_nested(cfg, ("paths", "data_gold", "root")))
    except KeyError as exc:
        errors.append(str(exc))
        return errors

    for p, label, must_be_dir in [
        (data_raw_root, "paths.data_raw.root", True),
        (datasets_root, "paths.data_raw.datasets.root", True),
        (bronze_root, "paths.data_bronze.root", True),
        (silver_root, "paths.data_silver.root", True),
        (gold_root, "paths.data_gold.root", True),
    ]:
        if not p.exists():
            errors.append(f"Path does not exist: {label} -> {p}")
        elif must_be_dir and not p.is_dir():
            errors.append(f"Path is not a directory: {label} -> {p}")

    if not paysim_file.exists():
        errors.append(f"Paysim dataset does not exist: paths.data_raw.datasets.paysim -> {paysim_file}")
    elif not paysim_file.is_file():
        errors.append(f"Paysim path is not a file: paths.data_raw.datasets.paysim -> {paysim_file}")

    return errors


def validate_config() -> List[str]:
    cfg = get_config()
    errors: List[str] = []
    errors.extend(validate_required_keys(cfg))
    errors.extend(validate_directories_and_files(cfg))
    return errors


if __name__ == "__main__":
    errs = validate_config()
    if errs:
        print("CONFIG VALIDATION FAILED")
        for e in errs:
            print(" -", e)
        sys.exit(1)
    else:
        print("CONFIG VALIDATION OK")
        sys.exit(0)
