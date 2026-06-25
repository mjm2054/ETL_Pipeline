# Data Ingestion Subsystem

This project is a Python-based data ingestion pipeline that reads a CSV file of video game sales data, cleans and validates it, removes duplicates, and loads the results into PostgreSQL staging tables. Invalid records are written to a reject table with a reason for rejection.

## Features

- Reads data from a CSV file using pandas.
- Normalizes column names.
- Consolidates duplicate game records by primary key.
- Validates required fields and data types.
- Loads valid data into PostgreSQL using UPSERT logic.
- Stores invalid rows in a reject table without duplicating rejects.
- Uses YAML for configuration and `.env` for database credentials.
- Uses structured logging instead of print statements.
- Includes unit tests for core transformation logic.

## Project Structure

```text
ETL_Cognizant/
  src/
    __init__.py
    config.py
    db.py
    readers.py
    clean.py
    validate.py
    load.py
    main.py
  config/
    config.yaml
  tests/
    test_clean.py
    test_validate.py
  .env
  .env.example
  requirements.txt
  README.md
```

## Requirements

- Python 3.10 or later
- PostgreSQL
- A virtual environment

## Setup

### 1. Create and activate the virtual environment

If you do not already have one:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

If `.venv` already exists, just activate it:

```bash
source .venv/bin/activate
```

### 2. Install dependencies

```bash
python3 -m pip install -r requirements.txt
```

## Configuration

### `.env`

Create a `.env` file in the project root with your database credentials:

```env
DB_NAME=etl_demo
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### `config/config.yaml`

The project uses YAML to define the CSV source and target tables:

```yaml
sources:
  - name: games_csv
    type: csv
    path: data/VGSales.csv
    target_table: stg_games
    reject_table: stg_games_rejects
    pk: [title]
```

## PostgreSQL Tables

Create the tables in PostgreSQL before running the ETL.

### `stg_games`

```sql
CREATE TABLE stg_games (
    title TEXT PRIMARY KEY,
    genre TEXT,
    publisher TEXT,
    developer TEXT,
    critic_score NUMERIC,
    total_sales NUMERIC,
    release_date DATE
);
```

### `stg_games_rejects`

```sql
CREATE TABLE stg_games_rejects (
    title TEXT,
    genre TEXT,
    publisher TEXT,
    developer TEXT,
    critic_score NUMERIC,
    total_sales NUMERIC,
    release_date DATE,
    reason TEXT,
    CONSTRAINT stg_games_rejects_title_reason_uk UNIQUE (title, reason)
);
```

## How It Works

1. The CSV is read into a pandas DataFrame.
2. Column names are cleaned and standardized.
3. Duplicate game rows are consolidated by title.
4. The data is validated for missing or invalid values.
5. Valid records are upserted into `stg_games`.
6. Rejected records are inserted into `stg_games_rejects` without duplicates.
7. Logging records each major step of the pipeline.

## Running the Project

From the project root, with your virtual environment activated:

```bash
python3 -m src.main
```

## Running Tests

If you want to run the unit tests:

```bash
PYTHONPATH=. python3 -m pytest
```

## Logging

The project uses Python’s built-in `logging` module instead of print statements. Logs show:
- rows read from the source file,
- rows after consolidation,
- valid vs rejected row counts,
- load progress,
- and completion status.

## Notes on Upsert

The main staging table uses `ON CONFLICT (title) DO UPDATE`, so rerunning the ETL updates existing rows instead of creating duplicates. The reject table uses `ON CONFLICT (title, reason) DO NOTHING` to prevent duplicate reject records.

## Troubleshooting

- If you get import errors, make sure you are running the command from the project root.
- If you get database errors, verify that PostgreSQL is running and the tables have been created.
- If the script cannot find packages, confirm your virtual environment is activated.

## Author

Mason Muscarello