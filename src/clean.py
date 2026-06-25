import pandas as pd
from .config import PK_COLUMNS

def consolidate_games(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["critic_score"] = pd.to_numeric(df["critic_score"], errors="coerce")
    df["total_sales"] = pd.to_numeric(df["total_sales"], errors="coerce")
    df["release_date"] = pd.to_datetime(
        df["release_date"],
        format="%d-%m-%Y",
        errors="coerce",
    )

    return (
        df.groupby(PK_COLUMNS, as_index=False)
        .agg(
            {
                "genre": "first",
                "publisher": "first",
                "developer": "first",
                "critic_score": "mean",
                "total_sales": lambda s: s.sum(min_count=1),
                "release_date": "min",
            }
        )
    )