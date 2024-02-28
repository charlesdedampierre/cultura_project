import math
import typing as t
import warnings

import pandas as pd
from data_model import Individual
from data_model_region import Country, CountryFiltered, Region
from functions_geo import point_to_coordonate
from sys_utils import load_model, save_model
from tqdm import tqdm

warnings.simplefilter(action="ignore", category=FutureWarning)

tqdm.pandas()


from dotenv import load_dotenv

load_dotenv()
import os

DATA_ENV_PATH = (
    os.getenv("DATA_ENV_PATH")
    + "/ENS - Cultural Index - Countries Databases - consolidate_table.csv"
)


def filter_space(row):
    if (
        (row["latitude"] <= row["max_latitude"])
        and (row["latitude"] >= row["min_latitude"])
        and (row["longitude"] <= row["max_longitude"])
        and (row["longitude"] >= row["min_longitude"])
    ):
        res = 1
    else:
        res = 0

    return res


def add_country_filter(x):
    if math.isnan(x["min_latitude"]):
        x["min_latitude"] = None

    if math.isnan(x["max_latitude"]):
        x["max_latitude"] = None

    if math.isnan(x["min_longitude"]):
        x["min_longitude"] = None

    if math.isnan(x["max_longitude"]):
        x["max_longitude"] = None

    return CountryFiltered(
        country=x["country_model"],
        min_year=x["min_date"],
        max_year=x["max_date"],
        min_latitude=x["min_latitude"],
        max_latitude=x["max_latitude"],
        min_longitude=x["min_longitude"],
        max_longitude=x["max_longitude"],
    )


def get_regions(path=DATA_ENV_PATH) -> t.List[Region]:
    df_region = pd.read_csv(path)

    df_region_model = (
        df_region[["region_code", "region", "space_based"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    df_region_model["region_model"] = df_region_model.apply(
        lambda x: Region(
            name=x["region"], code=x["region_code"], space_based=x["space_based"]
        ),
        axis=1,
    )
    df_region_model = df_region_model.drop("region", axis=1)
    region_model = list(df_region_model["region_model"])

    df_region["country_model"] = df_region.apply(
        lambda x: Country(name=x["country_name"], iso_a3=x["iso_a3"]), axis=1
    )

    df_region["country_filtered_model"] = df_region.apply(
        lambda x: add_country_filter(x), axis=1
    )
    df_region_new = df_region[["region_code", "region", "country_filtered_model"]]

    df_region_group = (
        df_region_new.groupby("region_code")["country_filtered_model"]
        .apply(list)
        .reset_index()
    )
    dict_region_group = df_region_group.to_dict(orient="records")
    dict_region_group = {
        x["region_code"]: x["country_filtered_model"] for x in dict_region_group
    }

    new_regions = []

    for reg in region_model:
        reg.countries_filtered = dict_region_group.get(reg.code)
        new_regions.append(reg)

    return new_regions


def get_individuals_regions(
    individuals: t.List[Individual], regions: t.List[Region]
) -> t.List[Individual]:
    # region_id_model = {x.code: x for x in regions}

    individual_country = [x for x in individuals if x.country != None]
    individual_country = [x for x in individual_country if x.impact_years != None]

    individual_country = [
        {
            "wiki_id": x.id.wikidata_id,
            "iso_a3": x.country.iso_a3,
            "range": x.impact_years,
        }
        for x in individual_country
    ]

    df_ind = pd.DataFrame(individual_country)

    df_ind["impact_year"] = df_ind["range"].apply(
        lambda x: [year for year in range(int(x[0]), int(x[1]) + 10, 10)]
    )
    df_ind = df_ind.explode("impact_year").reset_index(drop=True)
    df_ind = df_ind.drop("range", axis=1)

    df_reg_all = [
        {
            "iso_a3": [y.country.iso_a3 for y in x.countries_filtered],
            "region_code": x.code,
            "region_name": x.name,
            "spaced_based": x.space_based,
            "min_year": [y.min_year for y in x.countries_filtered],
            "max_year": [y.max_year for y in x.countries_filtered],
            "min_latitude": [y.min_latitude for y in x.countries_filtered],
            "max_latitude": [y.max_latitude for y in x.countries_filtered],
            "min_longitude": [y.min_longitude for y in x.countries_filtered],
            "max_longitude": [y.max_longitude for y in x.countries_filtered],
        }
        for x in regions
    ]

    df_reg_all = pd.DataFrame(df_reg_all)
    df_reg_all = df_reg_all.explode(
        [
            "iso_a3",
            "min_year",
            "max_year",
            "min_latitude",
            "max_latitude",
            "min_longitude",
            "max_longitude",
        ]
    ).reset_index(drop=True)

    df_reg = df_reg_all[df_reg_all["spaced_based"] == 0]

    # Transform min/max into a range to match individuals range
    df_reg["range"] = df_reg.apply(
        lambda row: [row["min_year"], row["max_year"]], axis=1
    )
    df_reg["impact_year"] = df_reg["range"].apply(
        lambda x: [year for year in range(int(x[0]), int(x[1]) + 10, 10)]
    )
    df_reg = df_reg.explode("impact_year").reset_index(drop=True)
    df_reg = df_reg.drop("range", axis=1)

    final_non_space = pd.merge(df_ind, df_reg, on=["iso_a3", "impact_year"])
    final_non_space = (
        final_non_space[["wiki_id", "region_code"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    individual_space = [x for x in individuals if x.id.raw_birthcities != None]
    individual_space = [x for x in individual_space if x.country != None]

    df_individual_space = pd.DataFrame(
        [
            {
                "wiki_id": x.id.wikidata_id,
                "iso_a3": x.country.iso_a3,
                "birthcity_location": [y.location for y in x.id.raw_birthcities],
                "range": x.impact_years,
            }
            for x in individual_space
        ]
    )

    df_individual_space = df_individual_space.explode("birthcity_location")
    df_individual_space = df_individual_space.dropna()
    df_individual_space["coordinate"] = df_individual_space[
        "birthcity_location"
    ].progress_apply(lambda x: point_to_coordonate(x))

    df_individual_space = df_individual_space.dropna().reset_index(drop=True)

    df_individual_space["longitude"] = df_individual_space["coordinate"].apply(
        lambda x: x[0]
    )
    df_individual_space["latitude"] = df_individual_space["coordinate"].apply(
        lambda x: x[1]
    )

    df_individual_space["impact_year"] = df_individual_space["range"].apply(
        lambda x: [year for year in range(int(x[0]), int(x[1]) + 10, 10)]
    )
    df_individual_space = df_individual_space.explode("impact_year").reset_index(
        drop=True
    )
    df_individual_space = df_individual_space.drop("range", axis=1)

    df_ref_space = df_reg_all[df_reg_all["spaced_based"] == 1].reset_index(drop=True)

    # Transform min/max into a range to match individuals range
    df_ref_space["range"] = df_ref_space.apply(
        lambda row: [row["min_year"], row["max_year"]], axis=1
    )
    df_ref_space["impact_year"] = df_ref_space["range"].apply(
        lambda x: [year for year in range(int(x[0]), int(x[1]) + 10, 10)]
    )
    df_ref_space = df_ref_space.explode("impact_year").reset_index(drop=True)
    df_ref_space = df_ref_space.drop("range", axis=1)

    final_space = pd.merge(
        df_ref_space, df_individual_space, on=["iso_a3", "impact_year"]
    )

    final_space["min_latitude"] = final_space["min_latitude"].fillna(-90)
    final_space["max_latitude"] = final_space["max_latitude"].fillna(90)
    final_space["min_longitude"] = final_space["min_longitude"].fillna(-180)
    final_space["max_longitude"] = final_space["max_longitude"].fillna(180)
    final_space["latitude"] = final_space["latitude"].astype(float)
    final_space["longitude"] = final_space["longitude"].astype(float)

    final_space["criteria"] = final_space.progress_apply(
        lambda x: filter_space(x), axis=1
    )
    final_space = final_space[final_space["criteria"] == 1].reset_index(drop=True)
    final_space = (
        final_space[["wiki_id", "region_code"]].drop_duplicates().reset_index(drop=True)
    )

    final = pd.concat([final_space, final_non_space]).reset_index(drop=True)

    """final["region_model"] = final["region_code"].progress_apply(
        lambda x: region_id_model.get(x)
    )"""

    final = final.groupby("wiki_id")["region_code"].progress_apply(list).reset_index()

    # Insert into individuals
    dict_final = final.to_dict(orient="records")
    dict_final = {x["wiki_id"]: x["region_code"] for x in dict_final}

    new_individuals = []

    for ind in individuals:
        ind.regions = dict_final.get(ind.id.wikidata_id)
        new_individuals.append(ind)

    return new_individuals


if __name__ == "__main__":
    from bunka_logger import logger

    CHECKPOINT_PATH = os.getenv("CHECKPOINT_PATH")

    logger.info("Get Region Model form.csv")
    regions = get_regions()
    save_model(regions, name=CHECKPOINT_PATH + "/regions.jsonl")

    logger.info("Load checkpoint number 4")
    individuals: t.List[Individual] = load_model(
        Individual, name=CHECKPOINT_PATH + "/checkpoint_3.jsonl"
    )
    logger.info("Get Region of Individuals")
    new_individuals: t.List[Individual] = get_individuals_regions(individuals, regions)

    logger.info("Save checkpoint number 5")
    save_model(new_individuals, name=CHECKPOINT_PATH + "/checkpoint_5.jsonl")

    """
    logger.info("Clean occupations")
    from functions_manual_regions import pipeline_manual_cleaning_region_global

    new_individuals = pipeline_manual_cleaning_region_global(new_individuals)
    save_model(new_individuals, name=CHECKPOINT_PATH + "/individuals.jsonl")

    """
