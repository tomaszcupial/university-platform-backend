from typing import Optional
import psycopg2
from background.logsconf import logger
from background.config import BaseConfig


#postgresql://postgres:postgres@localhost:5432/db 
def conn_to_db() -> Optional[psycopg2.connect]:
    """
    Nawiązuje połączenie z bazą danych.

    Funkcja próbuje nawiązać połączenie z bazą danych, korzystając z parametrów zdefiniowanych w konfiguracji. Jeżeli połączenie jest pomyślne, zwraca obiekt połączenia psycopg2. W przypadku niepowodzenia, zwraca None.

    Zwraca:
    psycopg2.extensions.connection: Obiekt połączenia psycopg2 reprezentujący połączenie z bazą danych.
    """

    try:
        return psycopg2.connect(dbname=BaseConfig.DB_NAME, user=BaseConfig.DB_USER, password=BaseConfig.DB_PASS, host=BaseConfig.DB_HOST, sslmode=BaseConfig.DB_SSL, options=f'-c search_path={BaseConfig.DB_SCHEMA}')
    except Exception as e:
        logger.info('Error durring connecting to database: %s' % e)





