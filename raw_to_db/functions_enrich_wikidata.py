from sys_utils import load_model
from data_model import RawIndividual, Individual
from functions_geo import get_country_model
from utils import round_nearest
import typing as t
import pandas as pd
from bunka_logger import logger
from tqdm import tqdm

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
    individual_birthcities = [
        {
            "individual_wikidata_id": x.id.wikidata_id,
            "country_location": [y.country_location for y in x.id.raw_birthcities],
        }
        for x in individuals
        if x.id.raw_birthcities != None
    ]
    df_individual_location = pd.DataFrame(individual_birthcities)
    df_individual_location = df_individual_location.explode("country_location")
    df_unique_locations = df_individual_location[["country_location"]].drop_duplicates()
    df_unique_locations["country_model"] = df_unique_locations[
        "country_location"
    ].progress_apply(lambda x: get_country_model(x))
    df_unique_locations = df_unique_locations.dropna()

    df_unique_locations["country_name"] = df_unique_locations["country_model"].apply(
        lambda x: x.name
    )

    df_final = pd.merge(
        df_individual_location, df_unique_locations, on="country_location"
    )
    df_final = df_final.drop_duplicates("individual_wikidata_id", keep="first")
    df_final["origin"] = "birthcity"
    df_final = df_final.rename(columns={"country_location": "location"})

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

    final = pd.concat([df_final_nationality, df_final])

    final = final.sort_values(
        ["individual_wikidata_id", "origin"], ascending=(False, True)
    )

    # first birthcity: ascending=(False, True)
    # first nationality: ascending=(False, False)

    final = final.drop_duplicates("individual_wikidata_id", keep="first").reset_index(
        drop=True
    )

    individual_country = final[["individual_wikidata_id", "country_model"]].to_dict(
        orient="records"
    )
    dict_individual_country = {
        x["individual_wikidata_id"]: x["country_model"] for x in individual_country
    }

    # Insert to the model
    new_individuals = []

    for ind in individuals:
        ind.country = dict_individual_country.get(ind.id.wikidata_id)
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
