import pandas as pd

def validate(df: pd.DataFrame):
    df = df.copy()

    for col in ["title", "genre", "publisher", "developer"]:
        df[col] = df[col].astype("string").str.strip()

    df["critic_score"] = pd.to_numeric(df["critic_score"], errors="coerce")
    df["total_sales"] = pd.to_numeric(df["total_sales"], errors="coerce")
    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")

    missing_title = df["title"].isna() | (df["title"] == "")
    missing_genre = df["genre"].isna() | (df["genre"] == "")
    missing_publisher = df["publisher"].isna() | (df["publisher"] == "")
    missing_developer = df["developer"].isna() | (df["developer"] == "")
    missing_critic_score = df["critic_score"].isna()
    missing_total_sales = df["total_sales"].isna()
    missing_release_date = df["release_date"].isna()

    valid_mask = (
        ~missing_title
        & ~missing_genre
        & ~missing_publisher
        & ~missing_developer
        & ~missing_critic_score
        & ~missing_total_sales
        & ~missing_release_date
    )

    valid_df = df.loc[valid_mask].copy()
    reject_df = df.loc[~valid_mask].copy()

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
        return "; ".join(reasons)

    if not reject_df.empty:
        reject_df["reason"] = reject_df.apply(build_reason, axis=1)
    else:
        reject_df["reason"] = pd.Series(dtype="string")

    return valid_df, reject_df