import sqlite3
import pandas as pd
import plotly.express as px
import sys
from plotly.subplots import make_subplots
import plotly.graph_objects as go

sys.path.append("../")
from functions_env import DB_PATH, DATA_PATH


conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()


time_resolution = 50

if __name__ == "__main__":
    df_individual = pd.read_sql_query(
        "SELECT * FROM individuals_main_information", conn
    )
    df_individual = df_individual[["individual_wikidata_id", "birthyear"]]
    df_individual_region = pd.read_sql_query("SELECT * FROM individuals_regions", conn)
    df_individual_region = df_individual_region[
        ["individual_wikidata_id", "region_name"]
    ].drop_duplicates()

    df_identifiers = pd.read_sql_query("SELECT * FROM identifiers", conn)
    df_identifiers["country_name"][df_identifiers["country_name"].isna()] = ""
    df_identifiers["identifier_name"] = df_identifiers.apply(
        lambda x: x["identifier_name"] + " (" + x["country_name"] + ")"
        if x["country_name"] != ""
        else x["identifier_name"],
        axis=1,
    )
    df_identifiers = df_identifiers.drop(
        ["country_wikidata_id", "count_records", "identifier_url"], axis=1
    ).drop_duplicates()

    df_country = pd.read_sql_query("SELECT * FROM country_continent", conn)
    df_country = df_country[["country_name", "continent_name"]]
    df_country = df_country.drop_duplicates("country_name", keep="first")
    df_identifiers = pd.merge(df_identifiers, df_country, on="country_name", how="left")

    df_ind_identifiers = pd.read_sql_query("SELECT * FROM individual_identifiers", conn)
    df_ind_identifiers = df_ind_identifiers.drop("identifier_name", axis=1)
    df_ind_identifiers = pd.merge(
        df_ind_identifiers, df_identifiers, on="identifiers_wikidata_id", how="left"
    )

    df_final = pd.merge(
        df_individual, df_ind_identifiers, on="individual_wikidata_id", how="left"
    )
    df_final = pd.merge(df_final, df_individual_region, on="individual_wikidata_id")

    df_final = df_final[~df_final["birthyear"].isna()]
    df_final["decade"] = df_final["birthyear"].apply(
        lambda x: int(x / time_resolution) * time_resolution
    )

    df_fig = df_final[
        [
            "individual_wikidata_id",
            "decade",
            "identifier_name",
            "country_name",
            "region_name",
        ]
    ]
    df_fig = (
        df_fig.groupby(["identifier_name", "country_name", "region_name", "decade"])[
            "individual_wikidata_id"
        ]
        .count()
        .rename("score")
        .reset_index()
    )

    df_fig.to_csv(DATA_PATH + "/df_identifiers_trends.csv")
