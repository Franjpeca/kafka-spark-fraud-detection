## Estructura del proyecto

kafka-spark-fraud-detection/
│
├── config.yaml
├── pytest.ini
├── requirements.txt
├── README.md
│
├── data/
│   ├── raw/
│   │   └── datasets/
│   │       └── paysim.csv
│   │
│   ├── bronze/
│   ├── silver/
│   └── gold/
│
├── logs/
│   ├── producer/
│   ├── spark/
│   ├── api/
│   ├── services/        # Kafka / Zookeeper / PostgreSQL
│   ├── maintenance/     # scripts auxiliares, validación, limpieza
│   └── archived/
│├── src/                      # todo el código fuente Python / lógica del proyecto
│   ├── config/               # carga/validación de configuración
│   │   ├── config_loader.py
│   │   └── validate_config.py
│   │
│   ├── utils/                # utilidades genéricas: logging, helpers, etc.
│   │   └── logging_setup.py
│   │
│   ├── preprocess/           # transformaciones “batch / ETL / limpieza / feature‑engineer”
│   │   └── preprocess_paysim.py
│   │
│   ├── producer/             # productor(s): lee datos desde data/raw → publica a Kafka (o similar)
│   │   └── paysim_producer.py
│   │
│   ├── spark/                # jobs / lógica de streaming / procesamiento con Spark
│   │   └── streaming_job.py
│   │
│   ├── api/                  # código de servicio / API / backend (si usas FastAPI u otro)
│   │   └── app.py
│   │
│   └── __init__.py
│
├── tests/
│   ├── config/
│   │   ├── test_config_loader.py
│   │   └── test_validate_config.py
│   │
│   ├── preprocess/
│   │   └── test_preprocess_paysim.py
│   │
│   ├── producer/
│   ├── spark/
│   ├── api/
│   ├── utils/
│   ├── __init__.py
│   └── test_imports.py
│
└── docker/
    ├── docker-compose.yaml
    └── Dockerfile_api
