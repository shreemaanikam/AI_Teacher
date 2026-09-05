#!/usr/bin/env python3
"""
Database Restore Utility for Apurva AI Teacher (Phase 11 Step 7 & 37).
Restores database tables from verified SHA256 backup snapshots.
"""

import os
import sys
import glob
import json
import hashlib
import sqlite3
import argparse
from sqlalchemy import text

# Add workspace to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import get_engine, get_database_url, init_db


def calculate_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def find_latest_backup(backup_dir: str = "data/backups") -> str | None:
    manifests = sorted(glob.glob(os.path.join(backup_dir, "*_manifest.json")))
    return manifests[-1] if manifests else None


def restore_database(manifest_path: str, dry_run: bool = False) -> bool:
    """Restores database tables from backup manifest with checksum verification."""
    if not os.path.exists(manifest_path):
        print(f"❌ Manifest not found: {manifest_path}")
        return False

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    print("=" * 65)
    print(f"🔄 APURVA DATABASE RESTORE — MANIFEST: {os.path.basename(manifest_path)}")
    print(f"📅 Timestamp: {manifest.get('timestamp')}")
    print(f"🛠️  DB Type  : {manifest.get('database_type')}")
    print(f"🔍 Dry Run  : {dry_run}")
    print("=" * 65)

    # 1. Verify file checksums
    backup_dir = os.path.dirname(manifest_path)
    for fname, expected_hash in manifest.get("checksums", {}).items():
        fpath = os.path.join(backup_dir, fname)
        if not os.path.exists(fpath):
            print(f"❌ Missing backup file: {fpath}")
            return False
        actual_hash = calculate_sha256(fpath)
        if actual_hash != expected_hash:
            print(f"❌ Checksum mismatch for {fname}! Expected {expected_hash}, got {actual_hash}")
            return False
        print(f"✅ Verified checksum for {fname}: OK")

    if dry_run:
        print("\n🔍 Dry-run complete. All backup files and checksums are 100% valid.")
        return True

    # 2. Perform Restore
    db_url = get_database_url()
    
    # If restoring SQLite and raw .db backup exists
    sqlite_backups = [f for f in manifest.get("files", []) if f.endswith(".db")]
    if db_url.startswith("sqlite") and sqlite_backups:
        raw_db_path = sqlite_backups[0]
        target_path = db_url.replace("sqlite:///", "")
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        
        # Safe restore using sqlite3 backup API
        with sqlite3.connect(raw_db_path) as src_conn, sqlite3.connect(target_path) as dst_conn:
            src_conn.backup(dst_conn)
        print(f"✅ Restored SQLite database directly to {target_path}")
        init_db()
        return True

    # Otherwise restore via JSON table import
    json_backups = [f for f in manifest.get("files", []) if f.endswith(".json") and not f.endswith("_manifest.json")]
    if not json_backups:
        print("❌ No valid JSON or DB snapshot found in manifest.")
        return False

    with open(json_backups[0], "r", encoding="utf-8") as f:
        table_data = json.load(f)

    init_db()
    engine = get_engine()

    with engine.begin() as conn:
        for tname, rows in table_data.items():
            if not isinstance(rows, list) or len(rows) == 0:
                continue
            # Delete existing rows and repopulate
            conn.execute(text(f"DELETE FROM {tname}"))
            cols = list(rows[0].keys())
            param_names = [f":{c}" for c in cols]
            insert_sql = text(f"INSERT INTO {tname} ({', '.join(cols)}) VALUES ({', '.join(param_names)})")
            conn.execute(insert_sql, rows)
            print(f"✅ Restored table {tname}: {len(rows)} records")

    print("\n🎉 Database restoration completed successfully with 0 errors.")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Apurva AI Teacher Database Restore")
    parser.add_argument("--manifest", type=str, help="Path to backup manifest JSON")
    parser.add_argument("--latest", action="store_true", help="Restore the latest available backup")
    parser.add_argument("--dry-run", action="store_true", help="Verify backup integrity without modifying database")
    args = parser.parse_args()

    target_manifest = args.manifest
    if args.latest or not target_manifest:
        target_manifest = find_latest_backup()

    if not target_manifest:
        print("❌ No backup manifest found in data/backups/")
        sys.exit(1)

    success = restore_database(target_manifest, dry_run=args.dry_run)
    sys.exit(0 if success else 1)
