"""
json_utils.py — JSON serialization helpers.

Enforces output conventions: UTF-8, stable key ordering, 2-space indent, trailing newline,
UTC timestamps with Z suffix, atomic writes.
"""

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def utc_now_iso() -> str:
    """Return current UTC time as ISO-8601 with Z suffix: '2026-03-23T15:42:00Z'."""
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:%SZ")


def to_stable_json(data: dict | list) -> str:
    """
    Serialize to JSON string with sort_keys=True, indent=2, ensure_ascii=False.
    Appends trailing newline.
    """
    return json.dumps(data, sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def write_json_atomic(path: Path, data: dict | list) -> None:
    """
    Write JSON to path using temp-file then atomic rename (os.replace).
    Enforces: UTF-8, stable key ordering, 2-space indent, trailing newline.
    Creates parent directories if they do not exist.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    content = to_stable_json(data).encode("utf-8")
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(content)
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise
