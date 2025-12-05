import yaml
from pathlib import Path
import functools
import os

@functools.lru_cache(maxsize=1)
def get_config():
    try:
        # Ir al directorio raíz del proyecto
        root_path = Path(__file__).resolve().parents[3]
        config_path = root_path / "config.yaml"
        
        if not config_path.exists():
            raise FileNotFoundError(f"El archivo de configuración no se encuentra en la ruta: {config_path}")
        
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        return cfg
    
    except FileNotFoundError as e:
        print(f"Error: {e}")
        raise
    except yaml.YAMLError as e:
        print(f"Error al cargar el archivo YAML: {e}")
        raise
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
        raise
