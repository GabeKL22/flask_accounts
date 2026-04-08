from pathlib import Path
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def _get_required_config(app, key: str):
    value = app.config.get(key)
    if value in (None, ""):
        raise RuntimeError(f"Missing required config: {key}")
    return value


def bootstrap_database(app, admin_user, admin_password, admin_db):
    db_host = app.config.get("DB_HOST", "localhost")
    db_port = app.config.get("DB_PORT", 5432)

    db_name = app.config["DB_NAME"]
    db_user = app.config["DB_USER"]
    db_password = app.config["DB_PASSWORD"]

    print(f"Connecting as admin_user={admin_user} admin_db={admin_db} host={db_host} port={db_port}")
    print(f"Target DB={db_name}, target user={db_user}")

    conn_kwargs = {
        "host": db_host,
        "port": db_port,
        "dbname": admin_db,
        "user": admin_user,
        "password": admin_password,
    }

    conn = psycopg2.connect(**conn_kwargs)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    try:
        cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (db_user,))
        user_exists = cur.fetchone() is not None
        print(f"user_exists={user_exists}")

        if not user_exists:
            cur.execute(
                sql.SQL("CREATE USER {} WITH PASSWORD %s").format(
                    sql.Identifier(db_user)
                ),
                (db_password,),
            )
            print(f"Created user: {db_user}")
        else:
            print(f"User already exists: {db_user}")

        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        db_exists = cur.fetchone() is not None
        print(f"db_exists={db_exists}")

        if not db_exists:
            cur.execute(
                sql.SQL("CREATE DATABASE {} OWNER {}").format(
                    sql.Identifier(db_name),
                    sql.Identifier(db_user),
                )
            )
            print(f"Created database: {db_name}")
        else:
            print(f"Database already exists: {db_name}")

        cur.execute(
            sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {}").format(
                sql.Identifier(db_name),
                sql.Identifier(db_user),
            )
        )
        print(f"Granted privileges on {db_name} to {db_user}")

    finally:
        cur.close()
        conn.close()


def init_schema(app) -> None:
    db_host = app.config.get("DB_HOST", "localhost")
    db_port = app.config.get("DB_PORT", 5432)

    db_name = _get_required_config(app, "DB_NAME")
    db_user = _get_required_config(app, "DB_USER")
    db_password = _get_required_config(app, "DB_PASSWORD")

    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        dbname=db_name,
        user=db_user,
        password=db_password,
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    try:
        schema_path = Path(__file__).resolve().parents[1] / "schema.sql"
        schema_sql = schema_path.read_text(encoding="utf-8")
        cur.execute(schema_sql)
    finally:
        cur.close()
        conn.close()