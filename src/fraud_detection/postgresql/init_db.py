import os
import socket
from dotenv import load_dotenv
import psycopg2
from pathlib import Path

from fraud_detection.config.config_loader import get_config
from fraud_detection.utils.logging_setup import get_logger

logger = get_logger(service_name="postgresql_init")

# ===========================
# CARGAR VARIABLES DE ENTORNO
# ===========================
# Cargar .env desde la raíz del proyecto
dotenv_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(dotenv_path)

# DEBUG: Mostrar lo que se ha cargado
logger.info("PG_PORT: %s", os.environ.get("PG_PORT"))
logger.info("PG_USER: %s", os.environ.get("PG_USER"))
logger.info("PG_PASSWORD: %s", os.environ.get("PG_PASSWORD"))
logger.info("PG_DB: %s", os.environ.get("PG_DB"))
logger.info("PG_HOST (env): %s", os.environ.get("PG_HOST"))

def init_db():
    # 1) Cargar configuración YAML
    cfg = get_config()
    db_cfg = cfg.get("postgresql", {})

    logger.info(f"PostgreSQL config raw: {db_cfg}")

    # 2) Variables de entorno para credenciales / puerto
    pg_port = os.environ.get("PG_PORT")
    pg_user = os.environ.get("PG_USER")
    pg_pass = os.environ.get("PG_PASSWORD")
    pg_db   = os.environ.get("PG_DB")

    # 3) Determinar host a usar
    # Preferir variable de entorno si existe
    env_host = os.environ.get("PG_HOST")
    config_host = db_cfg.get("host")

    # Si hay PG_HOST en entorno, usarlo
    if env_host:
        pg_host = env_host
        logger.info(f"Usando PG_HOST de entorno: {pg_host}")
    else:
        # Si no, intentar usar config_host y comprobar DNS
        pg_host = config_host
        try:
            socket.gethostbyname(pg_host)
            logger.info(f"Host desde config.yml resuelto OK: {pg_host}")
        except Exception:
            # Fallback automático a localhost
            logger.warning(
                f"Host '{pg_host}' no se resuelve localmente, usando fallback 'localhost'"
            )
            pg_host = "localhost"

    # 4) Validar variables necesarias
    missing = []
    if not pg_port:
        missing.append("PG_PORT")
    if not pg_user:
        missing.append("PG_USER")
    if not pg_pass:
        missing.append("PG_PASSWORD")
    if not pg_db:
        missing.append("PG_DB")
    if missing:
        logger.error(f"Faltan variables de entorno: {missing}")
        return

    # 5) Intentar conectar
    try:
        conn = psycopg2.connect(
            dbname=pg_db,
            user=pg_user,
            password=pg_pass,
            host=pg_host,
            port=int(pg_port),
        )
        logger.info("Conexión a PostgreSQL exitosa.")
    except Exception as e:
        logger.error(f"Error al conectar a PostgreSQL: {e}")
        return

    # 6) Ejecutar SQL de creación de tablas
    try:
        sql_path = Path(cfg["paths"]["postgresql_sql"]["create_tables"])
        logger.info(f"Leyendo script SQL desde: {sql_path}")

        with open(sql_path, "r", encoding="utf-8") as f:
            sql = f.read()

        with conn.cursor() as cur:
            cur.execute(sql)
            conn.commit()

        logger.info("Tablas creadas correctamente.")
    except Exception as e:
        logger.error(f"Error al ejecutar script SQL: {e}")
    finally:
        conn.close()
        logger.info("Conexión cerrada.")


def main():
    logger.info("=== INICIO INICIALIZACIÓN DE BASE DE DATOS ===")
    init_db()
    logger.info("=== FIN INICIALIZACIÓN DE BASE DE DATOS ===")


if __name__ == "__main__":
    main()
