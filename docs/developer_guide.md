# Developer Guide – kafka-spark-fraud-detection
Guía técnica para ejecutar y operar el proyecto durante el desarrollo.


# 1. Validar la configuración del proyecto
Antes de ejecutar cualquier componente, comprueba que `config.yaml` está completo
y que todas las rutas y ficheros existen.

Comando:

    python src/config/validate_config.py

Salida esperada:

    CONFIG VALIDATION OK

Si muestra errores, corrige el config o crea las carpetas que falten.


# 2. Cargar configuración desde cualquier script
Todos los scripts deben cargar rutas y parámetros así:

    from config.config_loader import get_config
    cfg = get_config()
    path = cfg["paths"]["data_raw"]["datasets"]["paysim"]


# 3. Scripts ETL (pendiente de ampliación)
En cuanto añadamos scripts ETL, se documentan aquí.

## 3.1 Preprocesamiento de PaySim (pendiente)
    python src/extract/<script>.py

## 3.2 Transformaciones adicionales (pendiente)
    python src/transform/<script>.py

## 3.3 Carga a capas (pendiente)
    python src/load/<script>.py


# 4. Kafka y generador de eventos (pendiente)
Cuando exista Docker Compose y el generador Kafka, añadir:

## 4.1 Levantar servicios
    docker compose up -d

## 4.2 Parar servicios
    docker compose down

## 4.3 Logs de Kafka
    docker logs kafka-broker -f

## 4.4 Ejecutar productor
    python src/producer/generate_events.py


# 5. Spark Streaming (pendiente)
Cuando el job esté preparado, añadir:

## 5.1 Ejecutar Spark en modo local
    spark-submit src/streaming/spark_stream.py

## 5.2 Ejecutar Spark en cluster (pendiente)
    spark-submit --master spark://localhost:7077 src/streaming/spark_stream.py


# 6. API FastAPI (pendiente)


# 7. Logging del proyecto (pendiente)
Cuando se implemente logging global, añadir aquí:

- ubicación de los logs
- comandos para verlos
- niveles recomendados
- formato y rotación


# 8. Tests (pendiente)
Cuando se añadan tests:

## 8.1 Ejecutar tests
    pytest -q

## 8.2 Ejecutar tests con cobertura (pendiente)
    pytest --cov=src


# 9. Utilidades (pendiente)
Comandos auxiliares que nunca fallan y ahorran tiempo:

- validar rutas
- limpiar directorios temporales
- preparar datasets de prueba


# 10. Comandos de mantenimiento (pendiente)
Para uso futuro:

- limpiar caches de Spark
- resetear topic de Kafka
- regenerar datos de ejemplo
- reconstruir contenedores Docker