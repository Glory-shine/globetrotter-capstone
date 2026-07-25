"""
Data Access Layer.

Provides thread-safe, atomic read/write access to the application's single
flat JSON file. A module-level RLock serializes access across the
threadpool workers FastAPI uses for sync code, and all I/O is additionally
pushed off the event loop via asyncio.to_thread so request handlers never
block on disk access. Writes are atomic (write-to-temp + os.replace) so a
crash or concurrent write can never leave the file half-written/corrupted.

The DB path can be overridden with the TRAVEL_APP_DB_PATH environment
variable, which is how the test-suite points the app at an isolated,
disposable file per test.
"""

import asyncio
import json
import os
import threading
from pathlib import Path
from typing import Any, Dict

_lock = threading.RLock()

DEFAULT_SCHEMA: Dict[str, Any] = {"users": [], "destinations": [], "itineraries": []}


def _get_data_path() -> Path:
    env_path = os.environ.get("TRAVEL_APP_DB_PATH")
    if env_path:
        return Path(env_path)
    return Path(__file__).resolve().parent / "data" / "db.json"


def _ensure_file(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(json.dumps(DEFAULT_SCHEMA, indent=2), encoding="utf-8")


def _read_sync() -> Dict[str, Any]:
    path = _get_data_path()
    with _lock:
        _ensure_file(path)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return dict(DEFAULT_SCHEMA)
        for key, default in DEFAULT_SCHEMA.items():
            data.setdefault(key, list(default))
        return data


def _write_sync(data: Dict[str, Any]) -> None:
    path = _get_data_path()
    with _lock:
        _ensure_file(path)
        tmp_path = path.with_suffix(".tmp")
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        os.replace(tmp_path, path)  # atomic on POSIX and Windows


async def read_data() -> Dict[str, Any]:
    """Read the full datastore. Safe to call concurrently."""
    return await asyncio.to_thread(_read_sync)


async def write_data(data: Dict[str, Any]) -> None:
    """Overwrite the full datastore atomically. Safe to call concurrently."""
    await asyncio.to_thread(_write_sync, data)
