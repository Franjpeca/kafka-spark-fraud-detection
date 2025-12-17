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

Contexto

En este proyecto, hemos implementado una simulación de eventos de transacciones financieras utilizando Kafka y Avro para estructurar los mensajes que se envían. La simulación simula diferentes tipos de transacciones financieras, cada una de ellas generada desde su productor correspondiente.

Productores y Tipos de Transacciones

Los productores gestionan distintos tipos de transacciones:

PAYMENT: Pagos entre cuentas.

CASH_IN: Depositar dinero en una cuenta.

CASH_OUT: Retirar dinero de una cuenta.

TRANSFER: Transferencias entre cuentas.

DEBIT: Pagos realizados a través de tarjeta de débito.

Uso de Avro

Cada tipo de transacción se estructura mediante un esquema Avro, que define los campos y su tipo. Los campos comunes incluyen:

transaction_id: Un identificador único para cada transacción.

step: El paso de la transacción.

type: El tipo de transacción (p.ej., "PAYMENT", "CASH_IN").

amount: Monto de la transacción.

nameorig y namedest: Nombres del origen y destino.

isfraud y isflaggedfraud: Indicadores de fraude.

timestamp: Fecha y hora de la transacción.

customer_id: Identificador del cliente.

source_system: Sistema que originó la transacción.

transaction_datetime: Fecha y hora en formato ISO 8601.

Simulación Multicanal

Se utiliza un enfoque multicanal, con un hilo independiente para cada productor, lo que permite que los diferentes tipos de transacciones se manejen de manera asíncrona y en paralelo, como si vinieran de múltiples canales de una empresa real. Cada productor simula la lectura de archivos Parquet que contienen los datos de las transacciones y los procesa con un delay aleatorio para simular la variabilidad en la llegada de los datos.

Generación de Eventos y Envío a Kafka

Los productores generan eventos a partir de los datos leídos de los archivos Parquet, los formatean según el esquema Avro, y los envían a Kafka para su consumo por otros servicios. El uso de UUIDs asegura que cada transacción tiene un identificador único. Los eventos son enviados con un delay aleatorio para simular tiempos de procesamiento variables.

Loggers y Monitorización

Cada productor y el simulador tienen su propio sistema de logs, lo que permite monitorear en detalle:

La lectura de archivos y el inicio de cada productor.

Los mensajes que se están generando y enviando.

Los errores y problemas en la transmisión de mensajes.

Los logs son gestionados por un logger central que maneja la rotación de archivos y asegura que los logs no se pierdan en caso de que el archivo crezca demasiado.

Flujo General

Simulación: El simulador lanza hilos para cada tipo de transacción (producción de mensajes) y genera eventos en paralelo.

Generación de Datos: Los productores leen archivos Parquet, procesan los datos y los formatean según el esquema Avro.

Envío de Datos a Kafka: Los eventos se envían a Kafka para ser consumidos por otros sistemas.

Logeo de Actividades: Cada productor y el simulador registran las actividades de la simulación en logs dedicados.

Conclusión

La implementación de estos productores y el uso de Kafka como intermediario permite simular una variedad de eventos financieros de forma asíncrona y distribuida, como si provinieran de múltiples canales en tiempo real.


# 2. Historico en PostgreSQL

Tendremos un "microservicios" usando PostgreSQL para guardar los eventos que vienen de Kafka. Para hacer esto, usamos Kafka Connect con un conector JDBC Sink, que se encarga de leer los mensajes de Kafka y almacenarlos directamente en PostgreSQL. Esto hace que no tengamos que escribir código extra para mover los datos entre Kafka y la base de datos, y asegura que los eventos se guarden de forma fiable.

El conector de Kafka Connect está configurado para insertar o actualizar los datos en PostgreSQL, evitando duplicados y asegurando que no se pierdan eventos si hay errores. De esta manera, podemos mantener un historial completo de los eventos y hacer consultas o análisis posteriores cuando sea necesario.

Se crea un conector de Kafka por cada topico, a través de Kafka Connect, pues cada topico se vuelca en su correspondiente tabla en la base de datos. 

Para lograr lo mencionado, debemos crear nuestra propia imagen de Kafka Connect porque la imagen base delega en el usuario añadir las funcionalidades que necesita, como el conector JDBC Sink y otros conectores que utilizaremos. Esto es lo que indica la documentación oficial de Kafka Connect. Al construir nuestra imagen personalizada, podemos agregar solo los conectores y configuraciones necesarias, como el soporte para PostgreSQL y MongoDB, asegurándonos de que todo funcione correctamente para nuestro proyecto sin tener que depender de una instalación manual de conectores en cada ejecución.

# 2. Métricas y dashboard en Grafana

Para las métricas en tiempo real se ha creado un microservicio independiente que consume directamente los mensajes de Kafka desde todos los topics de transacciones usando su propio consumer group. El propio servicio integra el consumidor y el cálculo de métricas, manteniendo contadores en memoria para obtener información básica como el número total de eventos, eventos por tipo, detección de IDs duplicados y errores de consumo. 

Estas métricas se exponen a través de un endpoint /metrics en formato Prometheus, que es scrappeado periódicamente. Grafana se conecta a Prometheus y permite visualizar los datos con distintos intervalos de refresco (por ejemplo cada 5 segundos o cada minuto), sin almacenar los eventos completos ni realizar cálculos en el dashboard. 

De esta forma se obtiene visibilidad en tiempo casi real del sistema, manteniendo esta parte separada del histórico en PostgreSQL y del procesamiento más complejo en Spark.

# 3. Resto de microservicios