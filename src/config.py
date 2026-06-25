from pathlib import Path
import os
import yaml
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

CONFIG_PATH = BASE_DIR / "config" / "config.yaml"
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CONFIG = yaml.safe_load(f)

GAMES_CFG = CONFIG["sources"][0]
CSV_PATH = GAMES_CFG["path"]
TARGET_TABLE = GAMES_CFG["target_table"]
REJECT_TABLE = GAMES_CFG["reject_table"]
PK_COLUMNS = GAMES_CFG["pk"]