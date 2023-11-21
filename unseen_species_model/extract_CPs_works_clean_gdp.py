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
    df_ind_regions = pd.read_sql_query("SELECT * FROM individuals_regions", conn)

    # Years
    df_ind = pd.read_sql_query("SELECT * FROM individuals_main_information", conn)
    df_ind_year = df_ind[["individual_wikidata_id", "birthyear"]].drop_duplicates()
    df_ind_year = df_ind_year.dropna()

    df_ind_year["productive_year"] = df_ind_year["birthyear"] + 35
    df_ind_year["decade"] = df_ind_year["productive_year"].apply(
        lambda x: round(x / 10) * 10
    )

    # NEWLY ADDED TO BE SURE WE ONLY KEEP INDIVIDUALS WITH A REFERENCE IN AN ONLINE CATALOG
    df_individuals = pd.read_sql_query("SELECT * FROM individuals_kept", conn)
    individuals_list = list(set(df_individuals["individual_wikidata_id"]))
    df = df_ind_year[df_ind_year["individual_wikidata_id"].isin(individuals_list)]

    df = pd.merge(df, df_ind_regions, on="individual_wikidata_id")
    df = df.drop_duplicates()

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
