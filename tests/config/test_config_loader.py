# Tests para el cargador de configuraciones del proyecto.
# Verifican que config.yaml se carga correctamente y contiene
# las claves esenciales de rutas del Data Lake.

from pathlib import Path
from fraud_detection.config.config_loader import get_config


def test_config_loads():
    """Test that get_config loads a dictionary."""
    cfg = get_config()
    assert isinstance(cfg, dict), "Config must be a dictionary"


def test_config_paths_exist():
    """Test that mandatory path keys exist."""
    cfg = get_config()

    assert "paths" in cfg, "Config must contain 'paths' key"
    assert "logs" in cfg["paths"], "Missing logs configuration"
    assert "data_raw" in cfg["paths"], "Missing data_raw section"
    assert "data_bronze" in cfg["paths"], "Missing data_bronze section"
    assert "data_silver" in cfg["paths"], "Missing data_silver section"
    assert "data_gold" in cfg["paths"], "Missing data_gold section"


def test_dataset_paths_exist_on_disk():
    """Test that dataset files exist on disk."""
    cfg = get_config()
    paysim_path = Path(cfg["paths"]["data_raw"]["datasets"]["paysim"])
    assert paysim_path.exists(), f"Dataset not found: {paysim_path}"
