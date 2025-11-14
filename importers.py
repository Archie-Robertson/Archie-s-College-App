"""Importers for external college/course databases.

This module provides helper functions to import competitor or course
data from common external formats: CSV, SQLite files, and SQL databases
(via SQLAlchemy connection strings). The importers normalize incoming
data to the application's expected schema and call `CollegeDatabase.add_competitor()`
to persist records.

Usage examples are in `IMPORTING_EXTERNAL_DB.md`.
"""
from typing import Dict, Optional
import csv
import json
import sqlite3
import os
from database import CollegeDatabase

try:
    from sqlalchemy import create_engine, text
except Exception:
    create_engine = None  # Optional dependency


def _normalize_programs(value: Optional[str]):
    """Normalize programs field: JSON list, or comma-separated string."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if not isinstance(value, str):
        return []
    value = value.strip()
    # If looks like JSON array
    if value.startswith('[') and value.endswith(']'):
        try:
            return json.loads(value)
        except Exception:
            pass
    # Otherwise split by comma
    return [p.strip() for p in value.split(',') if p.strip()]


def import_from_csv(file_path: str, column_map: Dict[str, str], db: CollegeDatabase):
    """Import competitor rows from a CSV file.

    Args:
        file_path: Path to CSV file with header row.
        column_map: Mapping from standard field names to CSV column names.
            Standard field names: college_id, name, location, latitude, longitude,
            programs, tuition, enrollment, acceptance_rate, avg_gpa, avg_sat,
            avg_act, source_url, metadata
        db: CollegeDatabase instance to persist records.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(file_path)

    with open(file_path, newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            data = {}
            for std_field, csv_col in column_map.items():
                data[std_field] = row.get(csv_col)

            # Normalize programs and metadata
            data['programs'] = _normalize_programs(data.get('programs'))
            meta = data.get('metadata')
            if meta and isinstance(meta, str):
                try:
                    data['metadata'] = json.loads(meta)
                except Exception:
                    data['metadata'] = {'raw_metadata': meta}
            else:
                data['metadata'] = data.get('metadata', {}) or {}

            # Convert numeric types where possible
            for key in ('tuition', 'enrollment', 'acceptance_rate', 'avg_gpa', 'avg_sat', 'avg_act', 'latitude', 'longitude'):
                val = data.get(key)
                if val in (None, '', 'NULL'):
                    data[key] = None
                    continue
                try:
                    if key in ('enrollment', 'avg_sat'):
                        data[key] = int(float(val))
                    else:
                        data[key] = float(val)
                except Exception:
                    data[key] = data.get(key)

            # Ensure college_id exists
            if not data.get('college_id'):
                # fallback to name slug
                data['college_id'] = (data.get('name') or '')[:100].replace(' ', '_').lower()

            db.add_competitor({
                'college_id': data.get('college_id'),
                'name': data.get('name'),
                'location': data.get('location'),
                'latitude': data.get('latitude'),
                'longitude': data.get('longitude'),
                'programs': data.get('programs', []),
                'tuition': data.get('tuition'),
                'enrollment': data.get('enrollment'),
                'acceptance_rate': data.get('acceptance_rate'),
                'avg_gpa': data.get('avg_gpa'),
                'avg_sat': data.get('avg_sat'),
                'avg_act': data.get('avg_act'),
                'source_url': data.get('source_url'),
                'metadata': data.get('metadata', {})
            })


def import_from_sqlite_file(sqlite_path: str, table_name: str, column_map: Dict[str, str], db: CollegeDatabase):
    """Import competitor rows from another SQLite database file.

    Args:
        sqlite_path: Path to the external SQLite file.
        table_name: Table name in the external DB to read rows from.
        column_map: Mapping from standard field names to external table column names.
        db: CollegeDatabase instance.
    """
    if not os.path.exists(sqlite_path):
        raise FileNotFoundError(sqlite_path)

    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()
    cols = ', '.join(column_map.values())
    query = f"SELECT {cols} FROM {table_name}"
    cursor.execute(query)
    rows = cursor.fetchall()
    col_names = [c[0] for c in cursor.description]

    for row in rows:
        ext = dict(zip(col_names, row))
        data = {}
        for std_field, ext_col in column_map.items():
            data[std_field] = ext.get(ext_col)

        data['programs'] = _normalize_programs(data.get('programs'))
        meta = data.get('metadata')
        if meta and isinstance(meta, str):
            try:
                data['metadata'] = json.loads(meta)
            except Exception:
                data['metadata'] = {'raw_metadata': meta}
        else:
            data['metadata'] = data.get('metadata', {}) or {}

        # Type conversions (same logic as CSV)
        for key in ('tuition', 'enrollment', 'acceptance_rate', 'avg_gpa', 'avg_sat', 'avg_act', 'latitude', 'longitude'):
            val = data.get(key)
            if val in (None, '', 'NULL'):
                data[key] = None
                continue
            try:
                if key in ('enrollment', 'avg_sat'):
                    data[key] = int(float(val))
                else:
                    data[key] = float(val)
            except Exception:
                data[key] = data.get(key)

        if not data.get('college_id'):
            data['college_id'] = (data.get('name') or '')[:100].replace(' ', '_').lower()

        db.add_competitor({
            'college_id': data.get('college_id'),
            'name': data.get('name'),
            'location': data.get('location'),
            'latitude': data.get('latitude'),
            'longitude': data.get('longitude'),
            'programs': data.get('programs', []),
            'tuition': data.get('tuition'),
            'enrollment': data.get('enrollment'),
            'acceptance_rate': data.get('acceptance_rate'),
            'avg_gpa': data.get('avg_gpa'),
            'avg_sat': data.get('avg_sat'),
            'avg_act': data.get('avg_act'),
            'source_url': data.get('source_url'),
            'metadata': data.get('metadata', {})
        })


def import_via_sqlalchemy(conn_string: str, query: str, column_map: Dict[str, str], db: CollegeDatabase):
    """Import using SQLAlchemy connection string and SQL query.

    This is optional and requires SQLAlchemy to be installed.
    """
    if create_engine is None:
        raise RuntimeError("SQLAlchemy is required for import_via_sqlalchemy. Install with: pip install sqlalchemy")

    engine = create_engine(conn_string)
    with engine.connect() as conn:
        res = conn.execute(text(query))
        rows = res.fetchall()
        keys = res.keys()
        for row in rows:
            ext = dict(zip(keys, row))
            data = {}
            for std_field, ext_col in column_map.items():
                data[std_field] = ext.get(ext_col)

            data['programs'] = _normalize_programs(data.get('programs'))
            meta = data.get('metadata')
            if meta and isinstance(meta, str):
                try:
                    data['metadata'] = json.loads(meta)
                except Exception:
                    data['metadata'] = {'raw_metadata': meta}
            else:
                data['metadata'] = data.get('metadata', {}) or {}

            # Numeric conversions
            for key in ('tuition', 'enrollment', 'acceptance_rate', 'avg_gpa', 'avg_sat', 'avg_act', 'latitude', 'longitude'):
                val = data.get(key)
                if val in (None, '', 'NULL'):
                    data[key] = None
                    continue
                try:
                    if key in ('enrollment', 'avg_sat'):
                        data[key] = int(float(val))
                    else:
                        data[key] = float(val)
                except Exception:
                    data[key] = data.get(key)

            if not data.get('college_id'):
                data['college_id'] = (data.get('name') or '')[:100].replace(' ', '_').lower()

            db.add_competitor({
                'college_id': data.get('college_id'),
                'name': data.get('name'),
                'location': data.get('location'),
                'latitude': data.get('latitude'),
                'longitude': data.get('longitude'),
                'programs': data.get('programs', []),
                'tuition': data.get('tuition'),
                'enrollment': data.get('enrollment'),
                'acceptance_rate': data.get('acceptance_rate'),
                'avg_gpa': data.get('avg_gpa'),
                'avg_sat': data.get('avg_sat'),
                'avg_act': data.get('avg_act'),
                'source_url': data.get('source_url'),
                'metadata': data.get('metadata', {})
            })