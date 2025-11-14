# Importing External College Databases

This guide explains how to connect or import colleges/courses data the college will give you, and how to feed it into the system.

Overview
- The project stores competitor colleges in SQLite (see `database.py` table `competitor_colleges`).
- You may receive data in one of several formats:
  - CSV / Excel (most common)
  - SQLite file
  - MySQL / PostgreSQL / MS SQL (live DB server)
  - JSON exports

This document shows three practical approaches you can use immediately:

1) Simple CSV import (recommended if they export CSV/Excel)
2) Direct SQLite import (if they give a SQLite file)
3) SQL import via connection string (MySQL/Postgres) — optional (requires SQLAlchemy)

All import helpers are implemented in `importers.py`.

---

Quick principles
- Map external column names to the app's expected fields (see mapping section below).
- Normalize program lists into a Python list of strings (CSV may be comma-separated or JSON array).
- Provide a unique `college_id` for each row; otherwise a slug of the name will be used.
- Validate coordinates (latitude/longitude) if provided.

---

Standard field names

When mapping columns, use these standard field names in the `column_map` you supply to the import helpers:

- college_id
- name
- location
- latitude
- longitude
- programs
- tuition
- enrollment
- acceptance_rate
- avg_gpa
- avg_sat
- avg_act
- source_url
- metadata

Example column map for CSV

Suppose CSV header row is: `id,inst_name,city,country,programs_list,students,tuition_usd`

Then column_map would be:

```python
column_map = {
    'college_id': 'id',
    'name': 'inst_name',
    'location': 'city',
    'programs': 'programs_list',
    'enrollment': 'students',
    'tuition': 'tuition_usd'
}
```

Then call:

```python
from importers import import_from_csv
from database import CollegeDatabase

db = CollegeDatabase()
import_from_csv('competitors.csv', column_map, db)
```

CSV notes
- `programs` may be a JSON array string (e.g. `["Computer Science","Business"]`) or a comma-separated string `Computer Science, Business`.
- `metadata` may be a JSON string; the importer will try to parse it.

---

SQLite file import

If the college provides a SQLite file (e.g. `college_dump.sqlite`) and a table (e.g. `courses` or `institutions`), use `import_from_sqlite_file`:

```python
from importers import import_from_sqlite_file
from database import CollegeDatabase

column_map = {
    'college_id': 'id',
    'name': 'name',
    'location': 'city',
    'programs': 'programs',
    'enrollment': 'students'
}

db = CollegeDatabase()
import_from_sqlite_file('college_dump.sqlite', 'institutions', column_map, db)
```

This will read rows and insert normalized competitors into your app's DB.

---

Import from live SQL server (MySQL/Postgres)

If the college gives you a connection string (e.g. `postgresql://user:pass@host:5432/dbname`) you can use `import_via_sqlalchemy`. This requires `sqlalchemy` to be installed in your environment.

Example:

```python
from importers import import_via_sqlalchemy
from database import CollegeDatabase

conn = 'postgresql://user:pass@host:5432/dbname'
query = 'SELECT id, name, city AS location, programs FROM institutions WHERE active=1'
column_map = {
    'college_id': 'id',
    'name': 'name',
    'location': 'location',
    'programs': 'programs'
}

db = CollegeDatabase()
import_via_sqlalchemy(conn, query, column_map, db)
```

Important security note: be careful with credentials. If you receive a connection string, prefer that they give you a read-only DB user and/or an exported file.

---

Mapping tips & troubleshooting

- Column name mismatches: inspect the CSV header or SQLite table schema first (open in a text editor or DB browser).
- Programs stored separately: sometimes programs are in a separate table (one-to-many). Export a flattened CSV with `institution_id` and `program_name`, then group by `institution_id` before calling the importer (or run a SQL query that aggregates programs into JSON/text list).
- Large imports: for very large datasets, run the import on a machine with sufficient memory and disk, and consider batching inserts.
- Encoding: ensure CSV is UTF-8. If not, open with the appropriate `encoding` argument.

---

When the college connects directly

If they can provide a database dump or a read-only connection, preferred workflows:
1. Best: ask for a CSV export (one file per table) — easiest and safest.
2. Next best: a SQLite file — very simple to import with the included helper.
3. If they insist on providing a live DB connection, ask for a read-only user and a connection string and run `import_via_sqlalchemy`.

Example requests to send the college

Please provide one of the following:
- A CSV file with a header row describing columns, and a short sample (first 10 rows).
- A SQLite file containing the institution table(s) and schema name(s).
- A read-only database user (connection string) and a sample SQL query returning the columns you want imported.

---

Next steps after import

1. Run the normal analysis flow: `python cli.py` → add any additional competitors or run analysis.
2. Verify imported records in the app: use the `cli` to generate the map or run `example_colleges_usage.py`.
3. If programs look wrong, inspect `programs` column values — adjust `column_map` or preprocess CSV to combine program rows.

---

If you want, I can also:
- Add a small helper to import programs when they come as a separate table (one-row-per-program).
- Add a CLI command to run CSV/SQLite imports from the project root.

If you'd like those, tell me which formats you expect and I will implement them next.
