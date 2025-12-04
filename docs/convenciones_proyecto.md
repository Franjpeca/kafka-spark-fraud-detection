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


## Importaciones

CONVENCIONES DE IMPORTACIÓN DEL PROYECTO

1. El proyecto usa estructura src/ con paquete instalado en editable.
   El nombre del paquete raíz es: fraud_detection

2. Todos los imports deben usar el paquete fraud_detection.
   Ejemplos correctos:
       from fraud_detection.config.config_loader import get_config
       from fraud_detection.preprocess.preprocess_paysim import preprocess
       from fraud_detection.utils.logging_setup import get_logger

3. Nunca usar imports basados en rutas físicas:
       NO: from src.config... 
       NO: import preprocess_paysim

4. Para ejecutar módulos internos, usar:
       python -m fraud_detection.<submodulo>.<script>

5. Tras clonar o actualizar el proyecto, instalar siempre en editable:
       pip install -e .

6. Los tests también deben usar imports basados en el paquete:
       from fraud_detection.config.config_loader import get_config
       from fraud_detection.preprocess.preprocess_paysim import preprocess

7. Todas las carpetas dentro de src/fraud_detection/ deben tener __init__.py
   para ser reconocidas como módulos importables.

Resumen:
Usar siempre imports basados en fraud_detection.
Nunca usar rutas relativas al directorio src/.


# Convenciones / Arquitectura — Microservicios & Flujo de Datos

## Arquitectura General

El sistema está diseñado con una **arquitectura de microservicios**, donde cada servicio tiene una **responsabilidad clara** y se comunica a través de **Kafka** como bus de eventos. Esto proporciona **escalabilidad**, **desacoplamiento** y **flexibilidad**.

## Microservicios Principales

1. **Productores de Kafka**  
   Publican eventos en Kafka (por ejemplo, transacciones de pago).

2. **Procesamiento en tiempo real (ej. Spark)**  
   Consume los eventos desde Kafka y aplica lógica de negocio, como la detección de fraude.

3. **Persistencia histórica**  
   Almacena los datos procesados de manera estructurada, usando bases de datos (MongoDB, PostgreSQL, etc.).

4. **Almacenamiento de logs / auditoría (opcional)**  
   Almacena eventos “raw” para trazabilidad y auditoría, permitiendo reconstruir el flujo de eventos.

5. **Servicio de métricas / estadísticas**  
   Calcula métricas y estadísticas en tiempo real o casi real, como volúmenes de transacciones, tasas de fraude, etc.

6. **Servicio de alertas**  
   Genera notificaciones o alertas cuando se detectan eventos críticos, como transacciones fraudulentas.

7. **API de consulta**  
   Expone los datos procesados a través de una API para su consulta por otros sistemas o usuarios.

## Ventajas de la Arquitectura

- **Escalabilidad independiente**: Cada servicio puede escalar por separado según sus necesidades.
- **Desacoplamiento**: Los servicios interactúan mediante Kafka y/o APIs, lo que facilita su desarrollo y mantenimiento independiente.
- **Flexibilidad**: Permite la evolución y adición de nuevos servicios sin afectar al sistema global.

## Flujo de Datos

1. Los **productores** publican eventos en Kafka.
2. Los **consumidores** (como **Spark**) procesan los datos en tiempo real.
3. Los **resultados procesados** se almacenan en la base de datos o se envían a otro servicio (alertas, métricas, etc.).
4. Los servicios de **notificación** y **API** exponen resultados o generan alertas.

## Notas

- Cada servicio tiene su propia base de datos o almacenamiento para evitar dependencias directas.
- El sistema se basa en **eventos** y **mensajería asíncrona** (Kafka) para asegurar desacoplamiento y resiliencia.

