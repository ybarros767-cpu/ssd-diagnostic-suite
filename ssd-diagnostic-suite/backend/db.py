from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import (JSON, Column, DateTime, Float, Integer, String, Text,
                        create_engine, select)
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from settings import settings


class Base(DeclarativeBase):
    pass


class Diagnostic(Base):
    __tablename__ = "diagnostics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_path: Mapped[str] = mapped_column(String(255), index=True)
    model: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    health: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    wear_level: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    temperature: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    read_speed: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    write_speed: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    power_on_hours: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    bad_blocks: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    results_json: Mapped[str] = mapped_column(Text)


_engine = None
_SessionLocal: sessionmaker[Session] | None = None


def _get_sqlite_path(url: str) -> Optional[str]:
    if url.startswith("sqlite:///"):
        # Example: sqlite:////app/data/app.db
        path = url.replace("sqlite:///", "")
        return path
    if url.startswith("sqlite:///"):
        return url.replace("sqlite:///", "")
    return None


def init_db() -> None:
    global _engine, _SessionLocal
    if settings.enable_db and _engine is None:
        # Ensure directory for SQLite
        sqlite_path = _get_sqlite_path(settings.database_url)
        if sqlite_path:
            os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)
        _engine = create_engine(settings.database_url, future=True)
        Base.metadata.create_all(_engine)
        _SessionLocal = sessionmaker(bind=_engine, expire_on_commit=False, future=True)


def _get_session() -> Session:
    if _SessionLocal is None:
        init_db()
    assert _SessionLocal is not None, "Database is not initialized"
    return _SessionLocal()


def save_diagnostic(results: Dict[str, Any], device_path: str) -> int:
    session = _get_session()
    try:
        metrics = results.get("metrics", {})
        diag = Diagnostic(
            device_path=device_path,
            model=results.get("device", {}).get("model", "Unknown"),
            health=metrics.get("health"),
            wear_level=metrics.get("wear_level"),
            temperature=metrics.get("temperature"),
            read_speed=metrics.get("read_speed"),
            write_speed=metrics.get("write_speed"),
            power_on_hours=metrics.get("power_on_hours"),
            bad_blocks=metrics.get("bad_blocks"),
            timestamp=datetime.fromisoformat(results.get("timestamp")) if results.get("timestamp") else datetime.utcnow(),
            results_json=json.dumps(results, ensure_ascii=False),
        )
        session.add(diag)
        session.commit()
        session.refresh(diag)
        return int(diag.id)
    finally:
        session.close()


def list_diagnostics(limit: int = 100) -> List[Dict[str, Any]]:
    session = _get_session()
    try:
        stmt = select(Diagnostic).order_by(Diagnostic.timestamp.desc()).limit(limit)
        rows = session.execute(stmt).scalars().all()
        return [
            {
                "id": int(r.id),
                "device_path": r.device_path,
                "model": r.model,
                "health": r.health,
                "wear_level": r.wear_level,
                "temperature": r.temperature,
                "read_speed": r.read_speed,
                "write_speed": r.write_speed,
                "power_on_hours": r.power_on_hours,
                "bad_blocks": r.bad_blocks,
                "timestamp": r.timestamp.isoformat(),
            }
            for r in rows
        ]
    finally:
        session.close()


def get_diagnostic(diagnostic_id: int) -> Optional[Dict[str, Any]]:
    session = _get_session()
    try:
        row = session.get(Diagnostic, diagnostic_id)
        if not row:
            return None
        return {
            "id": int(row.id),
            "device_path": row.device_path,
            "model": row.model,
            "health": row.health,
            "wear_level": row.wear_level,
            "temperature": row.temperature,
            "read_speed": row.read_speed,
            "write_speed": row.write_speed,
            "power_on_hours": row.power_on_hours,
            "bad_blocks": row.bad_blocks,
            "timestamp": row.timestamp.isoformat(),
            "results": json.loads(row.results_json or "{}"),
        }
    finally:
        session.close()
