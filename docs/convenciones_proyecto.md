
# Convenciones del Proyecto

## 1. Gestión de Rutas

Todas las rutas deben ser obtenidas desde `config.yaml` mediante la función `get_config()` ubicada en `src/config/config_loader.py`. No se permite hardcodear rutas dentro de los scripts. Si una ruta no existe en el config, debe añadirse allí antes de usarla.

## 2. Logging del Proyecto

Todos los servicios deben registrar sus logs en la carpeta `logs/` situada en la raíz del proyecto. Los logs no deben guardarse dentro de `src/`. Cada componente del sistema debe escribir únicamente en su propia carpeta de logs.

**Estructura acordada de logs:**
- `logs/producer/`: Registros del generador de eventos (productor Kafka)
- `logs/spark/`: Registros del job de Spark Streaming
- `logs/api/`: Registros de la API FastAPI
- `logs/services/`: Registros de servicios externos (Kafka, Zookeeper, PostgreSQL)
- `logs/maintenance/`: Registros de scripts auxiliares (validación, limpieza, preparación de datos)
- `logs/archived/`: Logs antiguos archivados o rotados

Los logs deben generarse siempre mediante el sistema de logging centralizado, evitando `print()` y usando el nombre del servicio correspondiente para mantener consistencia y trazabilidad.

## 3. Configuración y Secrets

**Configuración**: Las variables sensibles como credenciales y puertos se gestionan en el archivo `.env`. Las configuraciones internas (rutas de datos, estructuras de directorios) se colocan en `config.yml`.

**Secretos y Variables**: Se debe evitar almacenar valores sensibles directamente en el código. En su lugar, usar el archivo `.env` para gestionar las variables de entorno.

## 4. Tests

Por ahora, el proyecto utilizará la configuración `pythonpath` en `pytest.ini` para permitir imports estables durante el desarrollo. En el futuro, cuando el proyecto sea instalable o ejecutable por terceros, se migrará a una estructura profesional basada en `pyproject.toml` y una instalación editable (usando `pip install -e .`).

### Ejecución de Tests

Para ejecutar los tests, usa el siguiente comando:

```bash
pytest -q
```

Para ejecutar los tests con cobertura:

```bash
pytest --cov=src
```

## 5. Importaciones

**Convenciones de Importación**:

1. El proyecto usa estructura `src/` con paquete instalado en editable. El nombre del paquete raíz es: `fraud_detection`.
2. Todos los imports deben usar el paquete `fraud_detection`. Ejemplos correctos:
   ```python
   from fraud_detection.config.config_loader import get_config
   from fraud_detection.preprocess.preprocess_paysim import preprocess
   from fraud_detection.utils.logging_setup import get_logger
   ```
3. Nunca usar imports basados en rutas físicas:
   ```python
   NO: from src.config... 
   NO: import preprocess_paysim
   ```

4. Para ejecutar módulos internos, usar:

   ```bash
   python -m fraud_detection.<submodulo>.<script>
   ```

5. Tras clonar o actualizar el proyecto, siempre instalar en editable:

   ```bash
   pip install -e .
   ```

6. Los tests deben usar imports basados en el paquete.

## 6. Convenciones de Arquitectura — Microservicios & Flujo de Datos

El sistema está diseñado con una arquitectura de microservicios y se comunica a través de Kafka como bus de eventos. Esto permite escalabilidad, desacoplamiento y flexibilidad.

### Microservicios Principales

1. **Productores de Kafka**: Publican eventos en Kafka (ej., transacciones de pago).
2. **Procesamiento en tiempo real (Spark)**: Consume los eventos desde Kafka.
3. **Persistencia histórica**: Almacena los datos procesados (MongoDB, PostgreSQL, etc.).
4. **Almacenamiento de logs / auditoría**: Almacena eventos “raw” para trazabilidad y auditoría.
5. **Servicio de métricas**: Calcula métricas en tiempo real.
6. **Servicio de alertas**: Genera notificaciones o alertas en caso de eventos críticos.
7. **API de consulta**: Exposición de los datos procesados a través de una API.

**Ventajas**:
- Escalabilidad independiente para cada servicio.
- Desacoplamiento de servicios mediante Kafka y APIs.
- Flexibilidad para la evolución del sistema sin afectar a la estructura global.

## 7. Volúmenes de Docker

Los volúmenes se almacenan en la carpeta `volumes/`, separada de la carpeta `data/`, para evitar mezclar datos de dominio con datos persistentes de infraestructura.

**Estructura recomendada**:
- `data/`: Para datos de entrada y salida procesados.
- `volumes/`: Para volúmenes de contenedores Docker (Kafka, MongoDB, etc.).
- `logs/`: Para logs del sistema y servicios.

## 8. Configuración

Las variables sensibles van en `.env` y las configuraciones internas en `config.yml`.