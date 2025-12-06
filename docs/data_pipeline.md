# 0. Preprocesamiento de la información

Para poder simular datos bancarios reales, se toma un dataset sintético (PaySim) que es limpiado, normalizado y ampliado con ligeras características adicionales.  
Dado que el dataset original contiene más de 6 millones de registros, el procesamiento se realiza por chunks para evitar problemas de memoria.

Cada chunk procesado se divide en varios ficheros Parquet, uno por cada tipo de transacción (cash_in, cash_out, payment, etc.).  
Esto no solo resuelve la limitación de RAM, sino que además simula un escenario realista en el que una misma categoría de transacción procede de múltiples fuentes: cajeros, app móvil, web, POS, proveedores externos, etc.

El resultado final son múltiples Parquet por tipo, representando microfuentes independientes.  
Todos los ficheros se almacenan en la capa bronze del data lake, preparados para ser consumidos por distintos productores Kafka.


# 1. Kafka

A partir de los ficheros generados en bronze comienza la parte de ingesta en tiempo real.  
Kafka actúa como el bus de eventos principal del sistema, simulando cómo varias fuentes de datos publican transacciones bancarias en tiempo real.

Se definen varios productores Kafka: uno por cada tipo de transacción o por cada fuente simulada.  
Cada productor lee únicamente los ficheros Parquet que le corresponden y publica sus mensajes en el tópico adecuado, por ejemplo:
- transactions.cash_in  
- transactions.cash_out  
- transactions.payment

Cada mensaje se valida y publica siguiendo un esquema estructurado (JSON Schema o Avro) para asegurar consistencia y buenas prácticas.

En la parte consumidora, Kafka permite conectar múltiples microservicios.  
El consumidor principal es Spark Structured Streaming, que procesa los eventos en tiempo real.  
Además, se contemplan consumidores adicionales para simular una arquitectura distribuida, como servicios de auditoría, alertas o métricas.

Así, Kafka sirve como capa de desac acoplamiento entre fuentes y microservicios, y permite reproducir un pipeline de datos realista basado en eventos.
