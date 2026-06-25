import logging
import pandas as pd

from .config import TARGET_TABLE, REJECT_TABLE
from .db import get_connection

logger = logging.getLogger(__name__)


def _none(value):
    return None if pd.isna(value) else value


def load_items(df: pd.DataFrame) -> None:
    conn = get_connection()
    cur = conn.cursor()

    try:
        for row in df.itertuples(index=False):
            cur.execute(
                f"""
                INSERT INTO {TARGET_TABLE} (
                    title, genre, publisher, developer,
                    critic_score, total_sales, release_date
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (title)
                DO UPDATE SET
                    genre = EXCLUDED.genre,
                    publisher = EXCLUDED.publisher,
                    developer = EXCLUDED.developer,
                    critic_score = EXCLUDED.critic_score,
                    total_sales = EXCLUDED.total_sales,
                    release_date = EXCLUDED.release_date
                """,
                (
                    _none(row.title),
                    _none(row.genre),
                    _none(row.publisher),
                    _none(row.developer),
                    _none(row.critic_score),
                    _none(row.total_sales),
                    _none(row.release_date),
                ),
            )

        conn.commit()
        logger.info("Loaded %s rows into %s", len(df), TARGET_TABLE)
    finally:
        cur.close()
        conn.close()


def load_rejects(df: pd.DataFrame) -> None:
    if df.empty:
        logger.info("No rejected rows to load")
        return

    conn = get_connection()
    cur = conn.cursor()

    try:
        for row in df.itertuples(index=False):
            cur.execute(
                f"""
                INSERT INTO {REJECT_TABLE} (
                    title, genre, publisher, developer,
                    critic_score, total_sales, release_date, reason
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (title, reason)
                DO NOTHING
                """,
                (
                    _none(row.title),
                    _none(row.genre),
                    _none(row.publisher),
                    _none(row.developer),
                    _none(row.critic_score),
                    _none(row.total_sales),
                    _none(row.release_date),
                    _none(row.reason),
                ),
            )

        conn.commit()
        logger.info("Loaded %s rows into %s", len(df), REJECT_TABLE)
    finally:
        cur.close()
        conn.close()