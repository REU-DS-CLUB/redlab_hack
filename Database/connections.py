from psycopg import connect, connection
from psycopg.rows import dict_row
from sqlalchemy import create_engine
import os

from .vault import Settings

settings = Settings()


def get_connection() -> connection:
    """

    How to:

    with get_connection() as conn:
        with get_connection().cursor() as cur:
            cur.execute("SELECT * FROM raw;")
    conn.close()

    :return: pg connection object
    """

    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    dbname = os.getenv("POSTGRES_DATABASE")
    user = os.getenv("POSTGRES_USERNAME")
    password = os.getenv("POSTGRES_PASSWORD")

    cnn = connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password,
        row_factory=dict_row,
        autocommit=True
    )

    return cnn


def get_engine() -> connection:
    """

    How to:

    with get_connection() as conn:
        with get_connection().cursor() as cur:
            cur.execute("SELECT * FROM raw;")
    conn.close()

    :return: pg connection object
    """

    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    dbname = os.getenv("POSTGRES_DATABASE")
    user = os.getenv("POSTGRES_USERNAME")
    password = os.getenv("POSTGRES_PASSWORD")

    engine = create_engine(f"postgresql+psycopg://{user}:{password}@{host}:{port}/{dbname}")

    return engine
