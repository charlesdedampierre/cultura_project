import typing as t

import geopandas as gpd
import pandas as pd
from bunka_logger import logger
from data_model import Individual, RawIndividual
from data_model_region import Country
from functions_geo import get_country_model
from sys_utils import load_model
from tqdm import tqdm
from utils import round_nearest

tqdm.pandas()


def get_impact_years(individuals: t.List[Individual]) -> t.List[Individual]:
    individual_model_id = {x.id.wikidata_id: x for x in individuals}

    individuals_final = []
    for ind in individuals:
        minus25 = round_nearest(ind.id.birthyear + 35 - 25, 10)
        plus25 = round_nearest(ind.id.birthyear + 35 + 25, 10)
        impact_years = (minus25, plus25)

        new_ind = individual_model_id.get(ind.id.wikidata_id)
        new_ind.impact_years = impact_years
        individuals_final.append(new_ind)

    return individuals_final


def raw_to_individuals(raw_individuals: t.List[RawIndividual]) -> t.List[Individual]:
    indivuals_list = []
    for raw in raw_individuals:
        new_ind = Individual(id=raw)
        indivuals_list.append(new_ind)
    return indivuals_list


def get_country_code(individuals: t.List[Individual]) -> t.List[Individual]:
    # Birthcities
    individual_birthcities = [
        {
            "individual_wikidata_id": x.id.wikidata_id,
            "location": [y.location for y in x.id.raw_birthcities],
        }
        for x in individuals
        if x.id.raw_birthcities != None
    ]

    df_individual_location = pd.DataFrame(individual_birthcities)
    df_individual_location = df_individual_location.explode("location")
    df_individual_location = df_individual_location[
        df_individual_location["location"] != "nan"
    ]
    df_individual_location = df_individual_location.dropna()

    df_unique_locations = df_individual_location[["location"]].drop_duplicates()
    df_unique_locations["country_model"] = df_unique_locations[
        "location"
    ].progress_apply(lambda x: get_country_model(x))
    df_unique_locations = df_unique_locations.dropna()

    df_unique_locations["country_name"] = df_unique_locations["country_model"].apply(
        lambda x: x.name
    )

    df_final = pd.merge(df_individual_location, df_unique_locations, on="location")
    df_final_birthcities = df_final.drop_duplicates(
        "individual_wikidata_id", keep="first"
    )
    df_final_birthcities = df_final_birthcities[
        ["individual_wikidata_id", "country_name"]
    ].drop_duplicates()
    df_final_birthcities["origin"] = "birthcity"

    # Deathcities (There was an issue regarding the loading, hence the diffenrent way of loading)
    df_individual_location = pd.DataFrame(
        {
            "individual_wikidata_id": [x.id.wikidata_id for x in individuals],
            "deathcities": [x.id.raw_deathcities for x in individuals],
        }
    )
    df_individual_location = df_individual_location.dropna()
    df_individual_location = df_individual_location.explode("deathcities")

    def get_location_point(x):
        try:
            return x.location
        except:
            return None

    df_individual_location["location"] = df_individual_location["deathcities"].apply(
        lambda x: get_location_point(x)
    )
    df_individual_location = df_individual_location.dropna()
    df_individual_location = df_individual_location.drop("deathcities", axis=1)
    df_individual_location = df_individual_location.drop_duplicates()
    df_individual_location = df_individual_location.reset_index(drop=True)

    df_unique_locations = df_individual_location[["location"]].drop_duplicates()
    df_unique_locations["country_model"] = df_unique_locations[
        "location"
    ].progress_apply(lambda x: get_country_model(x))
    df_unique_locations = df_unique_locations.dropna()

    df_unique_locations["country_name"] = df_unique_locations["country_model"].apply(
        lambda x: x.name
    )

    df_final = pd.merge(df_individual_location, df_unique_locations, on="location")
    df_final_deathcities = df_final.drop_duplicates(
        "individual_wikidata_id", keep="first"
    )
    df_final_deathcities = df_final_deathcities[
        ["individual_wikidata_id", "country_name"]
    ].drop_duplicates()
    df_final_deathcities["origin"] = "deathcity"

    # Nationality
    individual_nationalities = [
        {
            "individual_wikidata_id": x.id.wikidata_id,
            "location": [y.location for y in x.id.raw_nationalities],
        }
        for x in individuals
        if x.id.raw_nationalities != None
    ]
    df_individual_location_nationality = pd.DataFrame(individual_nationalities)
    df_individual_location_nationality = df_individual_location_nationality.explode(
        "location"
    )

    df_unique_locations_nationality = df_individual_location_nationality[
        ["location"]
    ].drop_duplicates()
    df_unique_locations_nationality["country_model"] = df_unique_locations_nationality[
        "location"
    ].progress_apply(lambda x: get_country_model(x))
    df_unique_locations_nationality = df_unique_locations_nationality.dropna()

    df_unique_locations_nationality["country_name"] = df_unique_locations_nationality[
        "country_model"
    ].apply(lambda x: x.name)

    df_final_nationality = pd.merge(
        df_unique_locations_nationality,
        df_individual_location_nationality,
        on="location",
    )
    df_final_nationality["origin"] = "nationality"
    df_final_nationality = df_final_nationality[
        ["individual_wikidata_id", "country_name", "origin"]
    ].drop_duplicates()

    # Merging the three datasets
    final = pd.concat(
        [df_final_deathcities, df_final_nationality, df_final_birthcities]
    )
    order = ["deathcity", "birthcity", "nationality"]  # order to chose from

    sorting_key = lambda x: order.index(x) if x in order else float("inf")

    # Sort the DataFrame based on the 'origin' column using the custom key
    final = final.sort_values(by="origin", key=lambda x: x.map(sorting_key))
    final = final.drop_duplicates("individual_wikidata_id", keep="first")
    final = final.reset_index(drop=True)
    final = final.drop_duplicates()

    df_world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
    df_world["country_model"] = df_world.apply(
        lambda x: Country(name=x["name"], iso_a3=x["iso_a3"]), axis=1
    )
    df_world = df_world[["name", "country_model"]]
    df_world = df_world.rename(columns={"name": "country_name"})

    final = pd.merge(df_world, final, on="country_name")

    individual_country = final[["individual_wikidata_id", "country_model"]].to_dict(
        orient="records"
    )
    dict_individual_country = {
        x["individual_wikidata_id"]: x["country_model"] for x in individual_country
    }

    individual_country_origin = final[["individual_wikidata_id", "origin"]].to_dict(
        orient="records"
    )

    dict_individual_country_origin = {
        x["individual_wikidata_id"]: x["origin"] for x in individual_country_origin
    }

    # Insert to the model
    new_individuals = []

    for ind in individuals:
        ind.country = dict_individual_country.get(ind.id.wikidata_id)
        ind.country_data_origin = dict_individual_country_origin.get(ind.id.wikidata_id)
        new_individuals.append(ind)

    return new_individuals


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    import os

    CHECKPOINT_PATH = os.getenv("CHECKPOINT_PATH")

    logger.info("Load Checkpoint")
    raw_individuals: t.List[RawIndividual] = load_model(
        RawIndividual, name="individuals_filtered.jsonl"
    )
    raw_individuals = [x for x in raw_individuals if x.birthyear < 100]

    logger.info("From RawIndividuals to Individuals")
    individuals: t.List[Individual] = raw_to_individuals(raw_individuals)

    logger.info("Get Country Code")
    individuals: t.List[Individual] = get_country_code(individuals)
    print(len(individuals))

    logger.info("Get Impact years")
    individuals: t.List[Individual] = get_impact_years(individuals)
    print(len(individuals))

    logger.info("Save New checkpoint")
    from sys_utils import save_model

    save_model(individuals, name=CHECKPOINT_PATH + "/individuals_impact_country.jsonl")
