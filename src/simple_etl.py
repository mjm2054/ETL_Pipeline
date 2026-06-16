import pandas as pd
import psycopg2
from psycopg2.extensions import connection as PgConnection


DB_NAME = "etl_demo"
DB_USER = "masonmuscarello"
DB_PASSWORD = ""  # or set a real password if you add one
DB_HOST = "localhost"
DB_PORT = "5432"

CSV_PATH = "data/items.csv"


def get_connection() -> PgConnection:
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )


def read_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip().str.lower()
    #print(f"Read {len(df)} rows from {path}")
    print(df.columns.tolist())
    return df


def validate(df: pd.DataFrame):
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower()

    df["name"] = df["name"].astype(str).str.strip()
    df["id_num"] = pd.to_numeric(df["id"], errors="coerce")

    valid_mask = df["id_num"].notna() & (df["name"] != "")
    valid_df = df.loc[valid_mask, ["id_num", "name"]].copy()
    valid_df["id"] = valid_df["id_num"].astype(int)
    valid_df = valid_df[["id", "name"]]

    reject_df = df.loc[~valid_mask, ["id", "name"]].copy()
    reject_df["reason"] = ""
    reject_df.loc[df["id_num"].isna(), "reason"] = "invalid id"
    reject_df.loc[df["name"] == "", "reason"] = reject_df["reason"].mask(
        reject_df["reason"] == "", "blank name"
    )
    reject_df["reason"] = reject_df["reason"].replace("", "invalid row")

    print(f"validation: kept {len(valid_df)} rows, rejected {len(reject_df)} rows")
    return valid_df, reject_df

def load_items(df: pd.DataFrame) -> None:
    conn = get_connection()
    cur = conn.cursor()

    try:
        for row in df.itertuples(index=False):
            cur.execute(
                """
                INSERT INTO stg_items (id, name)
                VALUES (%s, %s)
                ON CONFLICT (id) DO UPDATE
                SET name = EXCLUDED.name
                """,
                (int(row[0]), row[1]),
            )

        conn.commit()
        print(f"Loaded {len(df)} rows into stg_items")
    finally:
        cur.close()
        conn.close()


def load_rejects(df: pd.DataFrame) -> None:
    if df.empty:
        print("No rejected rows to load")
        return

    conn = get_connection()
    cur = conn.cursor()

    try:
        for row in df.itertuples(index=False):
            cur.execute(
                """
                INSERT INTO stg_rejects (id, name, reason)
                VALUES (%s, %s, %s)
                """,
                (str(row.id), row.name, row.reason),
            )
        conn.commit()
        print(f"Loaded {len(df)} rows into stg_rejects")
    finally:
        cur.close()
        conn.close()

def main() -> None:
    df = read_csv(CSV_PATH)
    valid_df,reject_df = validate(df)
    load_items(valid_df)
    load_rejects(reject_df)


if __name__ == "__main__":
    main()