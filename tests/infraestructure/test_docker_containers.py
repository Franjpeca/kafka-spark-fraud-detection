# Test para verificar que los contenedores de Docker están corriendo y accesibles

import pytest
import subprocess
import socket

def test_docker_containers():
    # Lista de contenedores que queremos validar
    containers = ["zookeeper", "kafka", "spark-master", "spark-worker", "mongo"]
    
    # Verificar que cada contenedor está corriendo
    for container in containers:
        result = subprocess.run(
            ["docker", "ps", "--filter", f"name={container}", "--format", "'{{.Names}}'"],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"Error inspecting container {container}."
        assert container in result.stdout, f"{container} container is not running."

        # Verificar si el puerto de cada contenedor está disponible usando sockets
        if container == "zookeeper":
            port = 2181
        elif container == "kafka":
            port = 9092
        elif container == "spark-master":
            port = 7077
        elif container == "spark-worker":
            port = 7077
        elif container == "mongo":
            port = 27017

        # Verificar que el puerto de cada contenedor está accesible
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            result = s.connect_ex(('localhost', port))
            assert result == 0, f"Port {port} for {container} is not accessible. Connection refused."
