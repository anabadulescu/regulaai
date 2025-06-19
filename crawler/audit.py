import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON, MetaData, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker
from typing import Any, Dict, Optional

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/regulaai")
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Define audit_log table
audit_log = Table(
    "audit_log", metadata,
    Column("id", Integer, primary_key=True),
    Column("timestamp", DateTime(timezone=True), server_default=func.now(), nullable=False),
    Column("ip", String(64), nullable=True),
    Column("user_id", Integer, nullable=True),
    Column("action", String(128), nullable=False),
    Column("meta", JSON, nullable=True)
)
metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine)

def log_audit(event: str, user_id: int, meta: Dict[str, Any], ip: Optional[str] = None):
    session = SessionLocal()
    try:
        session.execute(
            audit_log.insert().values(
                timestamp=func.now(),
                ip=ip,
                user_id=user_id,
                action=event,
                meta=meta
            )
        )
        session.commit()
    finally:
        session.close() 