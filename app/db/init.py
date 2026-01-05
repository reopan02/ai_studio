from __future__ import annotations

from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.models.database import Base


async def init_db(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await _ensure_user_target_description_name_column(conn)


async def _ensure_user_target_description_name_column(conn) -> None:
    def _needs_name_column(sync_conn) -> bool:
        inspector = inspect(sync_conn)
        if "user_target_descriptions" not in inspector.get_table_names():
            return False
        columns = {col["name"] for col in inspector.get_columns("user_target_descriptions")}
        return "name" not in columns

    needs_name_column = await conn.run_sync(_needs_name_column)
    if not needs_name_column:
        return

    await conn.execute(
        text("ALTER TABLE user_target_descriptions ADD COLUMN name VARCHAR(100)")
    )
    await conn.execute(
        text(
            "UPDATE user_target_descriptions "
            "SET name = CASE "
            "WHEN description IS NOT NULL AND TRIM(description) <> '' "
            "THEN substr(description, 1, 100) "
            "ELSE 'Untitled' END "
            "WHERE name IS NULL OR name = ''"
        )
    )

