import sys

sys.path.append("../")

import numpy as np
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
    # Individuals' works
    df_ind_works = pd.read_sql_query("SELECT * FROM individual_created_work", conn)

    # Individuals Regions
    df_ind_regions = pd.read_sql_query("SELECT * FROM individuals_regions", conn)

    # Years
    df_ind = pd.read_sql_query("SELECT * FROM individuals_main_information", conn)
    df_ind_year = df_ind[["individual_wikidata_id", "birthyear"]].drop_duplicates()
    df_ind_year = df_ind_year.dropna()
    df_ind_year["decade"] = df_ind_year["birthyear"].apply(lambda x: round(x / 10) * 10)

    df = pd.merge(
        df_ind_works, df_ind_regions, on=["individual_wikidata_id", "individual_name"]
    )
    df = df[
        ["individual_wikidata_id", "work_wikidata_id", "region_code", "region_name"]
    ].drop_duplicates()
    df = pd.merge(df, df_ind_year, on="individual_wikidata_id")

    df_trends_works = (
        df.groupby(["region_name", "decade"])["work_wikidata_id"]
        .count()
        .rename("cultural_score")
        .reset_index()
    )
    df_trends_works["log_cultural_score"] = np.log(
        1 + df_trends_works["cultural_score"]
    )
    df_trends_works.to_csv(DATA_PATH + "/df_trends_works.csv")

    df_trends_individuals = df[
        ["individual_wikidata_id", "region_name", "decade"]
    ].drop_duplicates()
    df_trends_individuals = (
        df_trends_individuals.groupby(["region_name", "decade"])[
            "individual_wikidata_id"
        ]
        .count()
        .rename("cultural_score")
        .reset_index()
    )
    df_trends_individuals["log_cultural_score"] = np.log(
        1 + df_trends_individuals["cultural_score"]
    )
    df_trends_individuals.to_csv(DATA_PATH + "/df_trends_individuals.csv")

    df_count_work = (
        df_ind_works.groupby("individual_wikidata_id")["work_wikidata_id"]
        .count()
        .rename("count_works")
        .reset_index()
    )

    df_ind_regions = pd.read_sql_query("SELECT * FROM individuals_regions", conn)

    df = pd.merge(df_count_work, df_ind_year, how="outer")
    df = df.fillna(0)  # If no works, then put 0
    df = pd.merge(df, df_ind_regions, on="individual_wikidata_id")
    df = df.rename(columns={"count_works": "cultural_score"})

    df.to_csv(DATA_PATH + "/df_indi_works.csv")
