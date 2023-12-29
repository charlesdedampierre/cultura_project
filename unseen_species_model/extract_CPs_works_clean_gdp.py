import sys

sys.path.append("../")

import pandas as pd
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
    # Individuals Regions

    df = pd.read_csv("../immaterial_index/results/df_individuals_score.csv")

    # Clean the GDP Data
    df_clean_gdp = pd.read_sql_query("SELECT * FROM gdp_clean", conn)
    regions_clean = list(set(df_clean_gdp["region_code"]))
    df = df[df["region_code"].isin(regions_clean)]
    df = df[df["decade"] >= min(df_clean_gdp.year)]

    print(len(set(df.individual_wikidata_id)))

    # Load works of individuals

    df_ind_works = pd.read_sql_query("SELECT * FROM individual_created_work", conn)

    df_count_work = (
        df_ind_works.groupby("individual_wikidata_id")["work_wikidata_id"]
        .count()
        .rename("count_works")
        .reset_index()
    )
    df_final = pd.merge(df, df_count_work, on="individual_wikidata_id", how="left")
    df_final = df_final.fillna(0)  # When there is no works we add 0
    df_final.to_csv(DATA_PATH + "/df_indi_works_clean_gdp.csv")
