import pandas as pd
from pandas.testing import assert_frame_equal

from src.clean import consolidate_games


def test_consolidate_games_groups_by_title():
    df = pd.DataFrame(
        {
            "title": ["Mario", "Mario", "Zelda"],
            "genre": ["Action", "Action", "Adventure"],
            "publisher": ["Nintendo", "Nintendo", "Nintendo"],
            "developer": ["Nintendo", "Nintendo", "Nintendo"],
            "critic_score": [90, 80, 95],
            "total_sales": [10.0, 5.0, 20.0],
            "release_date": ["01-01-2020", "01-01-2020", "01-01-2021"],
        }
    )

    result = consolidate_games(df).sort_values("title").reset_index(drop=True)

    expected = pd.DataFrame(
        {
            "title": ["Mario", "Zelda"],
            "genre": ["Action", "Adventure"],
            "publisher": ["Nintendo", "Nintendo"],
            "developer": ["Nintendo", "Nintendo"],
            "critic_score": [85.0, 95.0],
            "total_sales": [15.0, 20.0],
            "release_date": pd.to_datetime(["01-01-2020", "01-01-2021"]),
        }
    ).sort_values("title").reset_index(drop=True)

    assert_frame_equal(result, expected)