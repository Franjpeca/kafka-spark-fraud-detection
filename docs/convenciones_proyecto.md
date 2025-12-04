# Convenciones del proyecto

## Gestión de rutas
Todas las rutas deben obtenerse desde `config.yaml` mediante la función 
`get_config()` ubicada en `src/config/config_loader.py`.

No se permite hardcodear rutas dentro de los scripts.
Si una ruta no existe en el config, debe añadirse allí antes de usarla.


## Logging del proyecto

Todos los servicios deben registrar sus logs en la carpeta `logs/` situada en la raíz del proyecto. 
Los logs no deben guardarse dentro de `src/` ni mezclarse con el código.

Estructura acordada:

logs/
  producer/      registros del generador de eventos (productor Kafka)
  spark/         registros del job de Spark Streaming
  api/           registros de la API FastAPI
  services/      registros de servicios externos (Kafka, Zookeeper, PostgreSQL, etc.)
  maintenance/   registros de scripts auxiliares (validación, limpieza, preparación de datos)
  archived/      logs antiguos archivados o rotados

Cada componente del sistema debe escribir únicamente en su propia carpeta de logs.

Los scripts auxiliares del proyecto, como validadores, preprocesadores o herramientas de mantenimiento,
deben registrar su actividad en `logs/maintenance/`.

Los logs se deben mantener separados por servicio para facilitar la depuración, trazabilidad
y futura integración con herramientas de observabilidad.

Los logs deben generarse siempre mediante el sistema de logging centralizado definido en el proyecto, evitando print() y usando el nombre de servicio correspondiente para mantener consistencia y trazabilidad.


## Sobre los test

Por ahora, el proyecto utilizará la configuración pythonpath en pytest.ini para permitir imports estables durante el desarrollo. Más adelante, cuando el proyecto deba ser instalable o ejecutable por terceros, se migrará a una estructura profesional basada en pyproject.toml y una instalación editable (pip install -e .).
