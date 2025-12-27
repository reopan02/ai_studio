from __future__ import annotations

import asyncio
import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.config import get_settings


def _normalize_pg_dump_url(database_url: str) -> str:
    url = str(database_url or "")
    url = url.replace("postgresql+asyncpg://", "postgresql://", 1)
    url = url.replace("postgresql+psycopg2://", "postgresql://", 1)
    url = url.replace("postgresql+psycopg://", "postgresql://", 1)
    return url


def _cleanup_old_backups(backup_dir: Path, retention_days: int) -> None:
    if retention_days <= 0:
        return
    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
    for p in backup_dir.glob("backup-*.dump"):
        try:
            mtime = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc)
        except FileNotFoundError:
            continue
        if mtime < cutoff:
            try:
                p.unlink()
            except FileNotFoundError:
                pass


def _run_pg_dump(output_path: Path) -> None:
    settings = get_settings()
    if not settings.DATABASE_URL:
        return

    backup_url = _normalize_pg_dump_url(settings.DATABASE_URL)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    cmd = [
        "pg_dump",
        "--no-owner",
        "--no-privileges",
        "--format=custom",
        "--file",
        str(output_path),
        backup_url,
    ]
    proc = subprocess.run(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if proc.returncode != 0:
        msg = proc.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(msg or "pg_dump failed")


async def run_backup_once() -> Path | None:
    settings = get_settings()
    if not settings.DATABASE_URL:
        return None
    if not settings.BACKUP_ENABLED:
        return None

    backup_dir = Path(settings.BACKUP_DIR)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = backup_dir / f"backup-{ts}.dump"

    await asyncio.to_thread(_run_pg_dump, output_path)
    await asyncio.to_thread(_cleanup_old_backups, backup_dir, settings.BACKUP_RETENTION_DAYS)
    return output_path


async def backup_loop(stop_event: asyncio.Event) -> None:
    settings = get_settings()
    interval = max(1, int(settings.BACKUP_INTERVAL_HOURS)) * 3600

    while not stop_event.is_set():
        try:
            await run_backup_once()
        except Exception:
            pass
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=interval)
        except asyncio.TimeoutError:
            continue

