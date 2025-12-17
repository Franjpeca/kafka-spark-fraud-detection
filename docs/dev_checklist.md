## Desarrollo de Kafka y microservicios

- [X] Configurar contenedores Docker (Kafka, Zookeeper, Mongo, etc.)
- [X] Crear un productor simple que lea datos de un archivo Parquet y los envíe a Kafka
- [X] Crear un consumidor básico que lea mensajes de Kafka y los imprima
- [X] Desarrollar el generador de eventos realista (para simular datos más realistas)

- [ ] Realizar test
- [ ] Implementar validación de esquemas y monitoreo (con herramientas como ELK o Prometheus)
- [ ] Realizar optimización del sistema



## Microservicio historico postgresql

### 1. Configuración del servicio PostgreSQL:
- [X] Instalar y configurar PostgreSQL.
- [X] Verificar que PostgreSQL esté en funcionamiento y accesible.
- [X] Configurar las credenciales de PostgreSQL en los secrets (host, puerto, usuario, contraseña).
- [X] Crear la base de datos y las tablas necesarias.
- [X] Verificar que las tablas se creen correctamente.

### 2. Configuración de Kafka Connect:
- [X] Instalar Kafka Connect.
- [ ] Configurar el conector JDBC Sink para PostgreSQL, incluyendo:
  - [X] Las credenciales de PostgreSQL (host, puerto, usuario, contraseña).
  - [X] El nombre de la base de datos.
  - [X] Los parámetros de inserción (upsert/insert).
- [X] Asegurar que el conector lea desde Kafka y guarde los datos en PostgreSQL.

### 3. Verificación del funcionamiento:
- [X] Verificar que los datos de Kafka lleguen correctamente a PostgreSQL:
  - [X] Asegurarse de que las credenciales y parámetros de `config.yml` sean correctos y estén funcionando.
- [X] Ejecutar pruebas simples para verificar que los datos se insertan correctamente en la base de datos.

### 4. Verificación final:
- [ ] Probar que el flujo completo funcione: los datos de Kafka deben llegar a PostgreSQL sin errores.
- [ ] Revisar los logs de Kafka Connect para confirmar que el conector funciona correctamente.

### 5. Script para automatizar el post

- [ ] Script para automatizar el deploy de los conectores




## Microservicio metricas y grafana

### 1. Configuracion del microservicio de metricas:
- [X] Definir el objetivo del microservicio (metricas simples en tiempo real).
- [X] Confirmar que no se almacenan eventos completos.
- [X] Definir las metricas a calcular (conteos, medias, tasas).
  - [ ] Total de eventos consumidos
  - [ ] Total de eventos por tipo (por topic)
  - [ ] Eventos por segundo / minuto (ventana configurable)
  - [ ] Ratio de cada tipo sobre el total
  - [ ] IDs duplicados detectados (contador + alerta)
  - [ ] Latencia media del evento (si hay timestamp)
  - [ ] Numero de errores de consumo / deserializacion
- [ ] Configurar variables de entorno y parametros en config.yml.

### 2. Configuracion de Kafka:
- [ ] Definir el topic o topics de Kafka a consumir.
- [ ] Crear un consumer group especifico para metricas.
- [ ] Configurar conexion a Kafka (broker, seguridad si aplica).
- [ ] Verificar que el consumidor lee mensajes correctamente.

### 3. Calculo de metricas en streaming:
- [ ] Implementar contadores en memoria (total y por tipo).
- [ ] Implementar acumuladores para medias.
- [ ] Definir ventana temporal de calculo (1s, 5s, etc).
- [ ] Implementar flush periodico de metricas.
- [ ] Verificar que no se guardan eventos en base de datos.

### 4. Sistema de metricas:
- [ ] Elegir sistema de metricas (Prometheus o InfluxDB).
- [ ] Configurar el sistema de metricas.
- [ ] Definir nombres de metricas y labels/tags.
- [ ] Verificar que las metricas se almacenan correctamente.

### 5. Integracion con Grafana:
- [ ] Instalar y configurar Grafana.
- [ ] Configurar datasource de metricas en Grafana.
- [ ] Crear dashboards basicos (conteos, medias, tasas).
- [ ] Ajustar intervalo de refresco.
- [ ] Verificar visualizacion en tiempo real.

### 6. Verificacion final:
- [ ] Probar el flujo completo (Kafka -> metricas -> Grafana).
- [ ] Revisar logs del microservicio de metricas.
- [ ] Confirmar latencia baja y estabilidad del sistema.