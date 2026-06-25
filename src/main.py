import logging

from .config import CSV_PATH
from .readers import read_csv
from .clean import consolidate_games
from .validate import validate
from .load import load_items, load_rejects

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)

logger = logging.getLogger(__name__)


def main():
    logger.info("ETL started")
    df = read_csv(CSV_PATH)
    logger.info("Rows read: %s", len(df))

    df = consolidate_games(df)
    logger.info("Rows after consolidation: %s", len(df))

    valid_df, reject_df = validate(df)
    logger.info("Valid rows: %s", len(valid_df))
    logger.info("Rejected rows: %s", len(reject_df))

    if not valid_df.empty:
        load_items(valid_df)
    if not reject_df.empty:
        load_rejects(reject_df)

    logger.info("ETL finished")


if __name__ == "__main__":
    main()