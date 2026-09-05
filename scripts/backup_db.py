#!/usr/bin/env python3
"""
Database Backup Utility for Apurva AI Teacher (Phase 11 Step 7 & 37).
Creates timestamped, SHA256-verified backup snapshots of all platform tables.
Supports both PostgreSQL and persistent SQLite databases.
"""

import os
import sys
import json
import time
import hashlib
import shutil
import sqlite3
from datetime import datetime, timezone
from sqlalchemy import inspect, text

# Add workspace to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import get_settings
from app.db.session import get_engine, get_database_url
from app.db import models


def calculate_sha256(filepath: str) -> str:
    """Calculates SHA256 checksum of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def backup_database(output_dir: str = "data/backups") -> dict:
    """Creates a verified database snapshot and metadata record."""
    os.makedirs(output_dir, exist_ok=True)
    timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    engine = get_engine()
    db_url = get_database_url()

    metadata = {
        "timestamp": timestamp_str,
        "database_type": "sqlite" if db_url.startswith("sqlite") else "postgresql",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "tables": {},
        "files": [],
        "checksums": {},
    }

    # 1. If SQLite, perform safe atomic backup using sqlite3.Connection.backup
    if db_url.startswith("sqlite"):
        source_path = db_url.replace("sqlite:///", "")
        if os.path.exists(source_path):
            raw_backup_path = os.path.join(output_dir, f"backup_{timestamp_str}.db")
            with sqlite3.connect(source_path) as src_conn, sqlite3.connect(raw_backup_path) as dst_conn:
                src_conn.backup(dst_conn)
            
            raw_checksum = calculate_sha256(raw_backup_path)
            metadata["files"].append(raw_backup_path)
            metadata["checksums"][os.path.basename(raw_backup_path)] = raw_checksum

    # 2. Universal JSON table export for portability and recovery
    json_export_path = os.path.join(output_dir, f"backup_{timestamp_str}.json")
    exported_data = {}

    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    with engine.connect() as conn:
        for tname in table_names:
            try:
                res = conn.execute(text(f"SELECT * FROM {tname}"))
                cols = res.keys()
                rows = []
                for row in res.fetchall():
                    row_dict = {}
                    for col_name, val in zip(cols, row):
                        if isinstance(val, (datetime, time)):
                            row_dict[col_name] = val.isoformat()
                        elif isinstance(val, (bytes, bytearray)):
                            row_dict[col_name] = val.hex()
                        else:
                            row_dict[col_name] = val
                    rows.append(row_dict)
                exported_data[tname] = rows
                metadata["tables"][tname] = len(rows)
            except Exception as e:
                metadata["tables"][tname] = f"error: {e}"

    with open(json_export_path, "w", encoding="utf-8") as f:
        json.dump(exported_data, f, indent=2)

    json_checksum = calculate_sha256(json_export_path)
    metadata["files"].append(json_export_path)
    metadata["checksums"][os.path.basename(json_export_path)] = json_checksum

    # 3. Write metadata manifest
    manifest_path = os.path.join(output_dir, f"backup_{timestamp_str}_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"✅ Backup completed successfully at {timestamp_str}")
    print(f"📦 Manifest: {manifest_path}")
    print(f"📊 Tables backed up: {list(metadata['tables'].keys())}")
    for fname, chk in metadata["checksums"].items():
        print(f"   - {fname} (SHA256: {chk[:16]}...)")

    return metadata


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "data/backups"
    backup_database(out)
