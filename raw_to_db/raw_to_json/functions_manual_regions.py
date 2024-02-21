import glob
import warnings

import numpy as np
import pandas as pd
from bunka_logger import logger
from tqdm import tqdm

warnings.simplefilter(action="ignore", category=FutureWarning)
import typing as t

from data_model import Individual
from dotenv import load_dotenv
from sys_utils import load_model, save_model
from tqdm import tqdm

load_dotenv()
import os

DATA_ENV_PATH = os.getenv("DATA_ENV_PATH")


adapted_country = {
    "Arab Countries": ["re_arabic_world", "re_muslim_world"],
    "Arab World": ["re_arabic_world", "re_muslim_world"],
    "Armenian": ["re_arabic_world", "re_muslim_world"],
    "Danish": [
        "re_nordic_countries",
        "re_western_europe",
        "re_northwestern_europe",
        "re_denmark",
    ],
    "English": ["re_united_kingdom", "re_western_europe", "re_northwestern_europe"],
    "French": ["re_france", "re_western_europe", "re_southwestern_europe"],
    "Greek ": ["re_greek_world", "re_greece"],
    "Greek World": ["re_greek_world", "re_greece"],
    "Indian Countries": ["re_indian_world"],
    "Italy": ["re_italy", "re_western_europe", "re_southwestern_europe"],
    "Latin World": ["re_latin"],
    "Low Countries": [
        "re_low_countries",
        "re_western_europe",
        "re_northwestern_europe",
    ],
    "Persian World": ["re_persian_world"],
    "Portugal": ["re_portugal", "re_western_europe", "re_southwestern_europe"],
    "Russian": ["re_eastern_europe", "re_slav_world"],
    "Russsian": ["re_eastern_europe", "re_slav_world"],
    "Spain": ["re_spain", "re_western_europe", "re_southwestern_europe"],
    "Spanish": ["re_spain", "re_western_europe", "re_southwestern_europe"],
    "Suisse": [
        "re_german_world",
        "re_western_europe",
        "re_northwestern_europe",
        "re_switzerland",
    ],
    "Turkish World": ["re_greek_world", "re_ottoman_turkey"],
    "UK": ["re_united_kingdom", "re_western_europe", "re_northwestern_europe"],
}


def pipeline_manual_cleaning_region_global(
    individuals: t.List[Individual],
) -> t.List[Individual]:
    # Get Exisiting Data
    df_wiki = [
        {"wikidata_id": x.id.wikidata_id, "region_code": x.regions} for x in individuals
    ]

    df_wiki = pd.DataFrame(df_wiki)
    df_wiki = df_wiki.explode("region_code")

    # Get new data
    df_wiki_new_region = _manual_cleaning_of_individuals(DATA_ENV_PATH)

    df_wiki_not_change = df_wiki[
        ~df_wiki["wikidata_id"].isin(list(set(df_wiki_new_region.wikidata_id)))
    ].reset_index(drop=True)
    df_wiki_new_region = df_wiki_new_region.rename(
        columns={"region_code_corrected": "region_code"}
    )
    merged_df = pd.concat([df_wiki_not_change, df_wiki_new_region])

    # group by

    merged_df = (
        merged_df.groupby(["wikidata_id"])["region_code"].apply(list).reset_index()
    )

    # Add manual cleaning
    manual_cleaning = pd.read_csv(
        DATA_ENV_PATH
        + "/manual_individuals_check/ENS - Cultural Index - Countries Databases - individuals_cleaned.csv"
    )

    manual_cleaning = manual_cleaning[["wikidata_id", "region_code_corrected"]]
    manual_cleaning["region_code_corrected"] = manual_cleaning[
        "region_code_corrected"
    ].apply(lambda x: x.split(","))

    merged_df = pd.merge(merged_df, manual_cleaning, on="wikidata_id", how="outer")
    merged_df.loc[merged_df["region_code_corrected"].notnull(), "region_code"] = (
        merged_df["region_code_corrected"]
    )
    merged_df = merged_df.drop("region_code_corrected", axis=1)

    # Fix the format of [None]
    df_all_ids = merged_df[["wikidata_id"]].copy()
    df_change_none = merged_df.explode("region_code")
    df_change_none["region_code"][df_change_none["region_code"] == "None"] = np.nan
    df_change_none = df_change_none.dropna()
    df_change_none = (
        df_change_none.groupby("wikidata_id")["region_code"].apply(list).reset_index()
    )

    merged_df = pd.merge(df_all_ids, df_change_none, on="wikidata_id", how="outer")

    # create a format to insert into the Indiviudal Model
    id_regions = {
        x["wikidata_id"]: x["region_code"] for x in merged_df.to_dict(orient="records")
    }

    logger.info("Replacing region_code for corrected individuals")

    for ind in tqdm(individuals):
        region = id_regions.get(ind.id.wikidata_id, None)

        if isinstance(region, list):
            ind.regions = region
        else:
            ind.regions = None

    return individuals


def _manual_cleaning_of_individuals(env_path=DATA_ENV_PATH):
    excel_file = pd.ExcelFile(
        env_path + "/manual_individuals_check/Golden Age - Individuals Check.xlsx"
    )
    all_data = pd.DataFrame()

    # loop through each sheet in the Excel file
    for sheet_name in excel_file.sheet_names:
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        all_data = pd.concat([all_data, df], ignore_index=True)

    df_old = all_data[["individual_id", "meta_country", "new_meta_country"]].copy()
    df_old = df_old.rename(columns={"individual_id": "wikidata_id"})

    # only select the columns that have been changed

    df_old = df_old.dropna().reset_index(drop=True)

    df_old["region_code_corrected"] = df_old["new_meta_country"].apply(
        lambda x: adapted_country.get(x)
    )

    df_old = df_old.drop(["meta_country", "new_meta_country"], axis=1)

    df_final = df_old.explode("region_code_corrected")
    df_final = df_final.drop_duplicates().reset_index(drop=True)

    return df_final


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    import os

    CHECKPOINT_PATH = os.getenv("CHECKPOINT_PATH")

    individuals: t.List[Individual] = load_model(
        Individual, name=CHECKPOINT_PATH + "/checkpoint_5.jsonl"
    )

    new_indivuals: t.List[Individual] = pipeline_manual_cleaning_region_global(
        individuals
    )

    save_model(new_indivuals, name=CHECKPOINT_PATH + "/individuals.jsonl")
