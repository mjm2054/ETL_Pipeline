import pandas as pd
import psycopg2
from psycopg2.extensions import connection as PgConnection


DB_NAME = "etl_demo"
DB_USER = "masonmuscarello"
DB_PASSWORD = ""  # or set a real password if you add one
DB_HOST = "localhost"
DB_PORT = "5432"

CSV_PATH = "data/VGSales.csv"


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

    columns_to_keep = [
        "title",
        "genre",
        "publisher",
        "developer",
        "critic_score",
        "total_sales",
        "release_date",
    ]

    df = df[columns_to_keep]

    print(df.columns.tolist())

    return df

def consolidate_games(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["critic_score"] = pd.to_numeric(
        df["critic_score"],
        errors="coerce"
    )

    df["total_sales"] = pd.to_numeric(
        df["total_sales"],
        errors="coerce"
    )

    df["release_date"] = pd.to_datetime(
        df["release_date"],
        format="%d-%m-%Y",
        errors="coerce"
    )

    consolidated_df = (
        df.groupby("title", as_index=False)
        .agg({
            "genre": "first",
            "publisher": "first",
            "developer": "first",
            "critic_score": "mean",
            "total_sales": lambda s: s.sum(min_count=1),
            "release_date": "min",
        })
    )

    return consolidated_df


def validate(df: pd.DataFrame):
    df = df.copy()

    # Clean text fields
    text_columns = [
        "title",
        "genre",
        "publisher",
        "developer",
    ]

    for col in text_columns:
        df[col] = df[col].astype(str).str.strip()

    # Convert numeric fields
    df["critic_score"] = pd.to_numeric(
        df["critic_score"],
        errors="coerce"
    )

    df["total_sales"] = pd.to_numeric(
        df["total_sales"],
        errors="coerce"
    )

    # Convert dates
    df["release_date"] = pd.to_datetime(
        df["release_date"],
        errors="coerce"
    )

    # ---- Split validation checks into separate masks ----
    missing_title = df["title"].isna() | (df["title"] == "")
    missing_genre = df["genre"].isna() | (df["genre"] == "")
    missing_publisher = df["publisher"].isna() | (df["publisher"] == "")
    missing_developer = df["developer"].isna() | (df["developer"] == "")
    missing_critic_score = df["critic_score"].isna()
    missing_total_sales = df["total_sales"].isna()
    missing_release_date = df["release_date"].isna()

    # Combine into one "valid" mask (same logic as before)
    valid_mask = (
        ~missing_title
        & ~missing_genre
        & ~missing_publisher
        & ~missing_developer
        & ~missing_critic_score
        & ~missing_total_sales
        & ~missing_release_date
    )

    # Valid rows
    valid_df = df.loc[valid_mask].copy()

    # Rejected rows
    reject_df = df.loc[~valid_mask].copy()

    # ---- Build detailed reject reasons ----
    def build_reason(row):
        reasons = []
        if pd.isna(row["title"]) or row["title"] == "":
            reasons.append("missing title")
        if pd.isna(row["genre"]) or row["genre"] == "":
            reasons.append("missing genre")
        if pd.isna(row["publisher"]) or row["publisher"] == "":
            reasons.append("missing publisher")
        if pd.isna(row["developer"]) or row["developer"] == "":
            reasons.append("missing developer")
        if pd.isna(row["critic_score"]):
            reasons.append("missing critic_score")
        if pd.isna(row["total_sales"]):
            reasons.append("missing total_sales")
        if pd.isna(row["release_date"]):
            reasons.append("missing release_date")
        # Join all reasons into a single string
        return "; ".join(reasons)

    if not reject_df.empty:
        reject_df["reason"] = reject_df.apply(build_reason, axis=1)
    else:
        reject_df["reason"] = []

    print(
        f"validation: kept {len(valid_df)} rows, "
        f"rejected {len(reject_df)} rows"
    )

    # quick summary of top reject reasons
    if not reject_df.empty:
        print("Top reject reasons:")
        print(reject_df["reason"].value_counts().head())

    return valid_df, reject_df

def load_items(df: pd.DataFrame) -> None:
    conn = get_connection()
    cur = conn.cursor()

    try:
        for row in df.itertuples(index=False):
            cur.execute(
                """
                INSERT INTO stg_games (
                    title, genre, publisher, developer,
                    critic_score, total_sales, release_date
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    row.title,
                    row.genre,
                    row.publisher,
                    row.developer,
                    row.critic_score,
                    row.total_sales,
                    row.release_date,
                ),
            )

        conn.commit()
        print(f"Loaded {len(df)} rows into stg_games")
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
                INSERT INTO stg_games_rejects (
                    title, genre, publisher, developer,
                    critic_score, total_sales, release_date, reason
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    str(row.title),
                    str(row.genre),
                    str(row.publisher),
                    str(row.developer),
                    str(row.critic_score),
                    str(row.total_sales),
                    str(row.release_date),
                    row.reason,
                ),
            )
        conn.commit()
        print(f"Loaded {len(df)} rows into stg_games_rejects")
    finally:
        cur.close()
        conn.close()

def main() -> None:
    df = read_csv(CSV_PATH)

    print(f"Rows before consolidation: {len(df)}")

    df = consolidate_games(df)

    print(f"Rows after consolidation: {len(df)}")
    

    valid_df, reject_df = validate(df)
    
    if not valid_df.empty:
        load_items(valid_df)
    if not reject_df.empty:
        load_rejects(reject_df)


if __name__ == "__main__":
    main()