from sqlalchemy import text, create_engine
from sqlalchemy.engine import Result
from config_db import user, password, host, port, db_name

def run_query(sql: str, params: dict = None):
    engine = create_engine(
        f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
    )

    with engine.connect() as conn:
        result: Result = conn.execute(text(sql), params or {})
        if result.returns_rows:
            return result.mappings().all()
        conn.commit()
        return None  # for INSERT/UPDATE/DELETE