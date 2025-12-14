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
- [ ] Instalar Kafka Connect.
- [ ] Configurar el conector JDBC Sink para PostgreSQL, incluyendo:
  - [ ] Las credenciales de PostgreSQL (host, puerto, usuario, contraseña).
  - [ ] El nombre de la base de datos.
  - [ ] Los parámetros de inserción (upsert/insert).
- [ ] Asegurar que el conector lea desde Kafka y guarde los datos en PostgreSQL.

### 3. Verificación del funcionamiento:
- [ ] Verificar que los datos de Kafka lleguen correctamente a PostgreSQL:
  - [ ] Asegurarse de que las credenciales y parámetros de `config.yml` sean correctos y estén funcionando.
- [ ] Ejecutar pruebas simples para verificar que los datos se insertan correctamente en la base de datos.

### 4. Verificación final:
- [ ] Probar que el flujo completo funcione: los datos de Kafka deben llegar a PostgreSQL sin errores.
- [ ] Revisar los logs de Kafka Connect para confirmar que el conector funciona correctamente.

