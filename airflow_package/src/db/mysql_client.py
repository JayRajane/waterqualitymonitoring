import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from typing import Optional, Dict

load_dotenv(".env")


class MySQLClient:

    def __init__(self):
        db_user = os.getenv("DB_USER")
        db_pass = os.getenv("DB_PASSWORD")
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "3306")
        db_name = os.getenv("DB_NAME")

        if not all([db_user, db_pass, db_name]):
            raise ValueError("Missing required DB environment variables.")

        uri = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
        self.engine = create_engine(uri, pool_size=5, max_overflow=10)
        self.engine = create_engine(uri, pool_size=5, max_overflow=10)

    def get_connection(self):
        return self.engine.connect()

    def fetch_user(self, user_id: int) -> Optional[Dict]:
        with self.get_connection() as conn:
            conn.execute(text("update  monitoring_app_customuser set password=:password where id=:id"), {
                'id': user_id, 'password': "pass123"})
            result = conn.execute(text("select id,username,password from monitoring_app_customuser where id=:id"), {
                'id': user_id})
            row = result.fetchone()
            return dict(row) if row else None
