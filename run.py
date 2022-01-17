from app import app
from waitress import serve

import os
import logging
import psycopg2

default_user_db = {
    "tables": [
        {
            "table_name": "users",
            "columns": ["userid", "username"],
        },
        {
            "table_name": "usertokens",
            "columns": ["userid", "tokenid", "token"],
        },
        {
            "table_name": "passwords",
            "columns": ["userid", "passwords"],
        },
    ]
}


def table_exists(conn, table_name):
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            exists(
                SELECT 
                    *
                FROM
                    information_schema.tables
                WHERE
                    table_name=%(table_name)s
            )
        """,
        {"table_name": table_name},
    )
    result = cur.fetchone()[0]

    logging.info(f"""{table_name} exists = {result}""")
    return result


def create_table(conn, table_dict):
    logging.info(f"""Creating {table_dict["table_name"]}""")


def create_tables_if_not_exists(conn, db_dict):
    for table_dict in db_dict["tables"]:
        if not table_exists(conn, table_dict["table_name"]):
            create_table(conn, table_dict)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filename="app.log",
        filemode="w",
    )

    conn = psycopg2.connect(
        os.environ.get("DATABASE_URL", "postgres://postgres:postgres@db:5432/postgres")
    )

    logging.debug("connected to database")

    create_tables_if_not_exists(conn, default_user_db)

    serve(app, host="0.0.0.0", port=8080, url_scheme="https")
