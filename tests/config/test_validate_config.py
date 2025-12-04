# Test de integración mínimo para el módulo validate_config.
# Comprueba que el script puede ejecutarse como módulo Python
# sin errores de importación ni fallos internos.

import subprocess
from pathlib import Path
import sys


def test_validate_config_script_runs():
    """Test that the validate_config module runs without crashing."""
    result = subprocess.run(
        [sys.executable, "-m", "fraud_detection.config.validate_config"],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, (
        f"validate_config.py returned an error:\n{result.stderr}"
    )
