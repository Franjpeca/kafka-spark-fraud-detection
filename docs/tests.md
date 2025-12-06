## 4. Tests

El proyecto utiliza pytest junto con la configuración pythonpath definida en pytest.ini, lo que permite importar módulos desde src/ sin necesidad de instalar el paquete durante el desarrollo.

Cuando el proyecto evolucione a un paquete instalable, los tests pasarán a ejecutarse desde una instalación editable (pip install -e .) definida en pyproject.toml.

### Ejecución de Tests

Para ejecutar todos los tests:
pytest -q

Para ejecutar con cobertura:
pytest --cov=src


# Tipos de Tests en el Proyecto

## Tests de Configuración

- test_config_loader.py  
  Verifica la carga correcta del archivo config.yaml.

- test_validate_config.py  
  Asegura que las rutas, claves y parámetros definidos en config.yaml sean válidos.


## Tests de Infraestructura

- test_docker_containers.py  
  Comprueba que los servicios esenciales (Kafka, Zookeeper, PostgreSQL…) estén ejecutándose antes de lanzar componentes dependientes.


## Tests de Preprocesamiento

Incluyen pruebas del flujo de entrada de datos antes de exponerlos a Kafka.

### test_preprocess_paysim.py
Verifica:
- Normalización de columnas
- Eliminación de duplicados
- Generación de timestamps
- Enriquecimiento con Faker
- Cohesión del registro resultante

### test_raw_dataset_structure.py
Comprueba que el dataset crudo tenga las columnas mínimas necesarias para el pipeline.

### test_preprocess_integration.py (Actualizado)
Este test valida el flujo completo del preprocesado chunked, pero usando un CSV pequeño sintético para:
- Evitar procesar PaySim real (6.3M filas)
- Mantener tiempos de test bajos
- Asegurar que se generan parquets válidos
- Validar el enriquecimiento y la separación por tipo
Los tests nunca deben depender de datasets masivos reales.


## Tests de Productor y Consumidor Kafka

- test_kafka_producer_consumer.py  
  Verifica que:
  - El productor envía mensajes correctamente
  - El consumidor los recibe sin errores
  - El flujo Kafka básico funciona en local


## Tests de API

- test_api.py (si existe o se añadirá)  
  Verifica que la API responde correctamente a peticiones GET/POST y maneja errores adecuadamente.


## Tests Generales

- test_imports.py  
  Garantiza que todos los módulos se pueden importar sin romper la arquitectura del proyecto.


## Tests de Utilidades

- test_utils.py  
  Comprueba que las funciones auxiliares del proyecto se comporten de forma estable y determinista.
