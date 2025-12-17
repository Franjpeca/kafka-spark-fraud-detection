FROM confluentinc/cp-kafka-connect:7.5.0

USER root

# Instalar JDBC Sink Connector
RUN confluent-hub install --no-prompt confluentinc/kafka-connect-jdbc:10.7.4

# Driver PostgreSQL
RUN curl -L https://jdbc.postgresql.org/download/postgresql-42.7.3.jar \
    -o /usr/share/confluent-hub-components/confluentinc-kafka-connect-jdbc/lib/postgresql.jar

USER appuser