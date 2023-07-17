import psycopg2
from config import BaseConfig
# Connect to the PostgreSQL database
def conn_to_db():
    return psycopg2.connect(dbname=BaseConfig.DB_NAME, user=BaseConfig.DB_USER, password=BaseConfig.DB_PASS, host=BaseConfig.DB_HOST, sslmode=BaseConfig.DB_SSL, options=f'-c search_path={BaseConfig.DB_SCHEMA}')
    
