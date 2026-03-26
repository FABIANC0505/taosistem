#!/usr/bin/env python3
"""
Migrate existing data from PostgreSQL to MySQL 8.

Safe flow:
  1. Run with --dry-run to validate source access and row counts.
  2. Review the reported table counts.
  3. Run without --dry-run to execute the migration.

Usage:
  set SOURCE_DATABASE_URL=postgresql://user:pass@host:5432/db
  set DATABASE_URL=mysql://root:pass@host:3306/bdtaosistem
  venv\Scripts\python.exe migrate_postgres_to_mysql.py --dry-run
  venv\Scripts\python.exe migrate_postgres_to_mysql.py
"""

from __future__ import annotations

import argparse
import json
import os
from decimal import Decimal
from typing import Any

from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.engine import Engine

from app.core.config import settings
from app.core.database import Base

import app.models.app_setting  # noqa: F401
import app.models.orden  # noqa: F401
import app.models.producto  # noqa: F401
import app.models.user  # noqa: F401

SOURCE_TABLES = ("users", "products", "app_settings", "orders")
TARGET_TRUNCATE_ORDER = ("orders", "products", "app_settings", "users")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Migrate PostgreSQL data into MySQL 8.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only validate connections and show row counts. No writes to MySQL.",
    )
    parser.add_argument(
        "--skip-truncate",
        action="store_true",
        help="Do not clear destination tables before inserting data.",
    )
    return parser.parse_args()


def normalize_source_url(url: str) -> str:
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+pg8000://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+pg8000://", 1)
    if url.startswith("postgresql+asyncpg://"):
        return url.replace("postgresql+asyncpg://", "postgresql+pg8000://", 1)
    return url


def normalize_target_url(url: str) -> str:
    if url.startswith("mysql+aiomysql://"):
        return url.replace("mysql+aiomysql://", "mysql+pymysql://", 1)
    if url.startswith("mysql://"):
        return url.replace("mysql://", "mysql+pymysql://", 1)
    return url


def get_source_url() -> str:
    source_url = (
        os.getenv("SOURCE_DATABASE_URL")
        or os.getenv("POSTGRES_SOURCE_URL")
        or os.getenv("POSTGRES_DATABASE_URL")
    )
    if not source_url:
        raise ValueError(
            "Define SOURCE_DATABASE_URL con la conexion PostgreSQL de origen."
        )
    return normalize_source_url(source_url)


def get_target_url() -> str:
    return normalize_target_url(settings.get_database_url())


def reflect_source_tables(engine: Engine) -> list[str]:
    metadata = MetaData()
    metadata.reflect(bind=engine)
    available = set(metadata.tables.keys())
    return [table for table in SOURCE_TABLES if table in available]


def count_rows(engine: Engine, table_name: str) -> int:
    with engine.connect() as connection:
        return connection.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar_one()


def serialize_json_if_needed(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return value


def normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    normalized = {}
    for key, value in row.items():
        if isinstance(value, Decimal):
            normalized[key] = float(value)
        else:
            normalized[key] = serialize_json_if_needed(value)
    return normalized


def fetch_rows(engine: Engine, table_name: str) -> list[dict[str, Any]]:
    with engine.connect() as connection:
        result = connection.execute(text(f"SELECT * FROM {table_name}"))
        return [normalize_row(dict(row)) for row in result.mappings()]


def create_target_schema(engine: Engine) -> None:
    Base.metadata.create_all(bind=engine)


def truncate_target_tables(engine: Engine) -> None:
    with engine.begin() as connection:
        connection.execute(text("SET FOREIGN_KEY_CHECKS=0"))
        for table_name in TARGET_TRUNCATE_ORDER:
            connection.execute(text(f"DELETE FROM {table_name}"))
        connection.execute(text("SET FOREIGN_KEY_CHECKS=1"))


def insert_rows(engine: Engine, table_name: str, rows: list[dict[str, Any]]) -> None:
    if not rows:
        print(f"{table_name}: sin registros para migrar")
        return
    columns = list(rows[0].keys())
    placeholders = ", ".join(f":{column}" for column in columns)
    quoted_columns = ", ".join(f"`{column}`" for column in columns)
    statement = text(
        f"INSERT INTO {table_name} ({quoted_columns}) VALUES ({placeholders})"
    )
    with engine.begin() as connection:
        connection.execute(statement, rows)
    print(f"{table_name}: {len(rows)} registros migrados")


def print_source_summary(engine: Engine, source_tables: list[str]) -> None:
    print("Resumen del origen PostgreSQL:")
    for table_name in SOURCE_TABLES:
        if table_name not in source_tables:
            print(f"- {table_name}: tabla no encontrada")
            continue
        print(f"- {table_name}: {count_rows(engine, table_name)} registros")


def migrate(dry_run: bool, skip_truncate: bool) -> None:
    source_engine = create_engine(get_source_url())
    target_engine = create_engine(get_target_url())

    try:
        source_tables = reflect_source_tables(source_engine)
        print(f"Tablas detectadas en origen: {', '.join(source_tables) or 'ninguna'}")
        print_source_summary(source_engine, source_tables)

        if dry_run:
            print("Dry run completado. No se escribieron datos en MySQL.")
            return

        create_target_schema(target_engine)
        if not skip_truncate:
            truncate_target_tables(target_engine)

        for table_name in SOURCE_TABLES:
            if table_name not in source_tables:
                print(f"{table_name}: tabla no encontrada en PostgreSQL, se omite")
                continue
            rows = fetch_rows(source_engine, table_name)
            insert_rows(target_engine, table_name, rows)

        print("Migracion completada")
    finally:
        source_engine.dispose()
        target_engine.dispose()


if __name__ == "__main__":
    args = parse_args()
    migrate(dry_run=args.dry_run, skip_truncate=args.skip_truncate)
