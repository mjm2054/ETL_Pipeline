import pandas as pd

from src.validate import validate


def test_validate_splits_valid_and_reject_rows():
    df = pd.DataFrame(
        {
            "title": ["Mario", "", "Zelda"],
            "genre": ["Action", "Adventure", "Adventure"],
            "publisher": ["Nintendo", "Nintendo", None],
            "developer": ["Nintendo", "Nintendo", "Nintendo"],
            "critic_score": [90, 80, 95],
            "total_sales": [10.0, 5.0, 20.0],
            "release_date": ["2020-01-01", "2020-01-02", None],
        }
    )

    valid_df, reject_df = validate(df)

    assert len(valid_df) == 1
    assert len(reject_df) == 2
    assert "reason" in reject_df.columns