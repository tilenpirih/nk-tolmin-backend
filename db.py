from playhouse.postgres_ext import PostgresqlExtDatabase
import os

def connect():
    return PostgresqlExtDatabase(database=os.getenv("DB_NAME", "postgres"), host=os.getenv("DB_HOST", "localhost"),
                        port=os.getenv("DB_PORT", 5432), user=os.getenv("DB_USER", "nktolmin"), password=os.getenv("DB_PASSWORD", "nktolmin"))

db = connect()