import os
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL chưa được set trong file .env")

engine: Engine = create_engine(DATABASE_URL, echo=False)  # echo=True nếu muốn xem SQL


def create_table_if_not_exists():
    """Tạo bảng articles"""
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,   
                title TEXT NOT NULL,
                link TEXT UNIQUE NOT NULL,
                crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.commit()
    print("✅ Bảng 'articles' đã được tạo/sửa cho SQLite (id tự tăng)!")