import sys

sys.path.append("../")

import pandas as pd
import numpy as np

from dotenv import load_dotenv

load_dotenv()
import os

import sqlite3

DB_PATH = os.getenv("DB_PATH")
DATA_PATH = "data"

conn = sqlite3.connect(DB_PATH)

if not os.path.exists(DATA_PATH):
    os.makedirs(DATA_PATH)

if __name__ == "__main__":
    # Individuals' works

    df_score = pd.read_sql_query("SELECT * FROM region_score", conn)
    df_score.to_csv("data/df_trends.csv")
