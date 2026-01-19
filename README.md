# Detección de fraude en transacciones bancarias en tiempo real


* EN DESARROLLO


- Este proyecto pretende establecer varios microservicios destinados a usar un modelo para detectar fraude en varios tipos de transacciones, pagos, etc.
- Se busca una arquitectura basada en microservicios, donde cada uno tenga una responsabilidad concreta
- Los microservicios utilizan Apache Kafka para leer y escribir eventos.
- El microservicio principal es Apache Spark, que busca transacciones bancarias y se alimentan a un modelo para dar una predicción en tiempo real de fraude o no fraude.
- Se implementan otros microservicios como dashboard de métricas y base de datos de historicos, simulando necesidades de un negoció y entornos profesionales.
