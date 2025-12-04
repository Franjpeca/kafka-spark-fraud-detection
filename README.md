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
│
├── src/
│   ├── config/
│   │   ├── config_loader.py
│   │   └── validate_config.py
│   │
│   ├── utils/
│   │   └── logging_setup.py
│   │
│   ├── preprocess/                    
│   │   ├── preprocess_paysim.py       # limpieza + feature engineering del CSV
│   │   └── helpers.py                 # funciones auxiliares opcionales
│   │
│   ├── producer/
│   │   └── paysim_producer.py         # envía eventos a Kafka
│   │
│   ├── spark/
│   │   └── streaming_job.py           # Spark Structured Streaming
│   │
│   ├── api/
│   │   └── app.py                     # FastAPI
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
