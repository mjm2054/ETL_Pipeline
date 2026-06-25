import pandas as pd

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
    return df[columns_to_keep]