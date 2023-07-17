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

    