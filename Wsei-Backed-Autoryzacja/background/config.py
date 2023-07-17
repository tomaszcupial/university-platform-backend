from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv
import os


class BaseConfig():
    load_dotenv()
    # db_config
    SECRET_KEY = os.getenv('SECRET_KEY')
    DB_USER = os.getenv('DB_USER')
    DB_PASS = os.getenv('DB_PASS')
    DB_NAME = os.getenv('DB_NAME')
    DB_PORT = os.getenv('DB_PORT')
    DB_HOST = os.getenv('DB_HOST')
    DB_SSL = os.getenv('DB_SSL')
    DB_SCHEMA = os.getenv('DB_SCHEMA')
    # postgresql://postgres:postgres@localhost:5432/db

    engine = create_engine("postgresql://"+DB_USER+":"+DB_PASS +
                           "@"+DB_HOST+":"+DB_PORT+"/"+DB_NAME, poolclass=NullPool,
                           pool_pre_ping=True, pool_recycle=10, connect_args={'sslmode': DB_SSL})
