import pandas as pd
from data_model import (
    ExternalID,
    Individual,
    Occupation,
    RawBirthcity,
    RawDeathcity,
    RawIndividual,
    RawNationality,
)
from functions_wikidata_load import (
    load_birthcity_country,
    load_deathcity,
    load_individual_id_occupation_id,
    load_individual_info,
    load_nationality_location,
    load_occupation_information,
)
from sys_utils import save_model
from tqdm import tqdm

tqdm.pandas()
import typing as t
import warnings

from sys_utils import load_model
from utils import clean_date, split_wiki

warnings.simplefilter(action="ignore", category=FutureWarning)

from dotenv import load_dotenv

load_dotenv()
import os

WIKIDATA_RAW_DATA = os.getenv("WIKIDATA_RAW_DATA")


def get_individual_main_wikidata_information() -> t.List[RawIndividual]:
    df_occupation_name = load_occupation_information()
    df_individual_id_occupation_id = load_individual_id_occupation_id()
    df_individual_id_occupation_id = df_individual_id_occupation_id.drop(
        "individual_name", 1
    ).drop_duplicates()

    df_occupation = pd.merge(
        df_occupation_name, df_individual_id_occupation_id, on="occupation_id"
    )
    df_occupation = (
        df_occupation.drop("individual_id", 1).drop_duplicates().reset_index(drop=True)
    )
    df_occupation = (
        df_occupation.groupby(["occupation_id", "occupation_name"])[
            "occupation_category"
        ]
        .apply(list)
        .reset_index()
    )

    # Occupation
    occupations_list = []
    for row in df_occupation.to_dict(orient="records"):
        wikidata_id = row["occupation_id"]
        name = row["occupation_name"]
        category = row["occupation_category"]

        occupation = Occupation(wikidata_id=wikidata_id, name=name, category=category)
        occupations_list.append(occupation)

    occupation_id_occupation_model = {x.wikidata_id: x for x in occupations_list}

    individual_info = load_individual_info()
    nationality_coordinate = load_nationality_location()

    # Start with nationality

    df_nationality = (
        individual_info[["nationality_id", "nationalityLabel"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    df_nationality = df_nationality.dropna()
    df_nationality = pd.merge(
        df_nationality, nationality_coordinate, on="nationality_id", how="outer"
    )

    nationality_list = []
    for row in df_nationality.to_dict(orient="records"):
        wikidata_id = row.get("nationality_id")
        name = row.get("nationalityLabel")
        location = row.get("location")

        nationality = RawNationality(
            wikidata_id=wikidata_id, name=name, location=location
        )
        nationality_list.append(nationality)

    nationality_id_nationality_model = {x.wikidata_id: x for x in nationality_list}

    data_birthcity_country = load_birthcity_country()

    df_birthcity = (
        individual_info[["birthcity_id", "birthcityLabel"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    df_birthcity = df_birthcity.dropna()
    df_birthcity = pd.merge(
        df_birthcity, data_birthcity_country, on="birthcity_id", how="outer"
    )

    birthcity_list = []
    for row in df_birthcity.to_dict(orient="records"):
        wikidata_id = row["birthcity_id"]
        name = row["birthcityLabel"]
        country_wikidata_id = row["country_wikidata_id"]
        country_location = row["country_location"]
        country_name = row["countryLabel"]
        location = row["location"]

        birthcity = RawBirthcity(
            wikidata_id=wikidata_id,
            name=name,
            country_wikidata_id=country_wikidata_id,
            country_location=country_location,
            location=location,
            country_name=country_name,
        )

        birthcity_list.append(birthcity)

    birthcity_id_birthcity_model = {x.wikidata_id: x for x in birthcity_list}

    df_nationality_individual = (
        individual_info[["wiki_id", "nationality_id"]]
        .dropna()
        .drop_duplicates()
        .reset_index(drop=True)
    )
    df_nationality_individual["nationality_model"] = df_nationality_individual[
        "nationality_id"
    ].apply(lambda x: nationality_id_nationality_model.get(x))
    df_nationality_individual = (
        df_nationality_individual.groupby("wiki_id")["nationality_model"]
        .apply(list)
        .reset_index()
    )
    dict_nationality_individual = df_nationality_individual[
        ["wiki_id", "nationality_model"]
    ].to_dict(orient="records")
    dict_nationality_individual = {
        x["wiki_id"]: x["nationality_model"] for x in dict_nationality_individual
    }

    df_birthcity_individual = (
        individual_info[["wiki_id", "birthcity_id"]]
        .dropna()
        .drop_duplicates()
        .reset_index(drop=True)
    )
    df_birthcity_individual["birthcity_model"] = df_birthcity_individual[
        "birthcity_id"
    ].apply(lambda x: birthcity_id_birthcity_model.get(x))
    df_birthcity_individual = (
        df_birthcity_individual.groupby("wiki_id")["birthcity_model"]
        .apply(list)
        .reset_index()
    )
    dict_birthcity_individual = df_birthcity_individual[
        ["wiki_id", "birthcity_model"]
    ].to_dict(orient="records")

    dict_birthcity_individual = {
        x["wiki_id"]: x["birthcity_model"] for x in dict_birthcity_individual
    }

    df_individual_occupation = df_individual_id_occupation_id.copy()
    df_individual_occupation["occupation_model"] = df_individual_occupation[
        "occupation_id"
    ].apply(lambda x: occupation_id_occupation_model.get(x))
    df_individual_occupation = (
        df_individual_occupation.groupby("individual_id")["occupation_model"]
        .apply(list)
        .reset_index()
    )
    dict_individual_occupation = df_individual_occupation.to_dict(orient="records")
    dict_individual_occupation = {
        x["individual_id"]: x["occupation_model"] for x in dict_individual_occupation
    }

    individuals_list = []
    for ind in tqdm(set(individual_info["wiki_id"])):
        wikidata_id = ind
        raw_nationalities = dict_nationality_individual.get(ind)
        raw_birthcities = dict_birthcity_individual.get(ind)
        occupations = dict_individual_occupation.get(ind)

        individual = RawIndividual(
            wikidata_id=ind,
            occupations=occupations,
            raw_nationalities=raw_nationalities,
            raw_birthcities=raw_birthcities,
        )
        individuals_list.append(individual)

    genders = individual_info[["wiki_id", "genderLabel"]].dropna().drop_duplicates()
    genders = genders.groupby("wiki_id")["genderLabel"].apply(list).reset_index()
    genders = genders.to_dict(orient="records")
    genders_dict = {x["wiki_id"]: x["genderLabel"] for x in genders}

    dates = individual_info[["wiki_id", "birthdateLabel"]].dropna().drop_duplicates()
    dates["birthyear"] = dates["birthdateLabel"].apply(lambda x: clean_date(x))
    dates = dates.dropna()
    dates = dates.drop_duplicates(["wiki_id", "birthyear"], keep="first").reset_index(
        drop=True
    )
    dates = dates.to_dict(orient="records")
    dates_dict = {x["wiki_id"]: x["birthyear"] for x in dates}

    names = load_individual_id_occupation_id()
    names = names[["individual_name", "individual_id"]].drop_duplicates()
    names = names.drop_duplicates("individual_id", keep="first")
    names = names.to_dict(orient="records")
    names_dict = {x["individual_id"]: x["individual_name"] for x in names}

    new_individuals = []
    for ind in tqdm(individuals_list):
        ind.gender = genders_dict.get(ind.wikidata_id, None)
        ind.birthyear = dates_dict.get(ind.wikidata_id, None)
        ind.name = names_dict.get(ind.wikidata_id, None)

        new_individuals.append(ind)

    # Add the deathcity information
    df_deathcity_ind, final_deathcity = load_deathcity()

    deathcity_list = []
    for row in final_deathcity.to_dict(orient="records"):
        wikidata_id = row["wikidata_id"]
        name = row["name"]
        country_wikidata_id = row["country_wikidata_id"]
        # country_location = row["country_location"]
        country_name = row["contry_name"]
        location = row["location"]

        deathcity = RawDeathcity(
            wikidata_id=wikidata_id,
            name=name,
            country_wikidata_id=country_wikidata_id,
            # country_location=country_location,
            location=location,
            country_name=country_name,
        )

        deathcity_list.append(deathcity)

    deathcity_id_deathcity_model = {x.wikidata_id: x for x in deathcity_list}
    df_deathcity_ind["deathcity_model"] = df_deathcity_ind["deathcity"].apply(
        lambda x: deathcity_id_deathcity_model.get(x)
    )

    df_deathcity_ind = df_deathcity_ind.dropna()

    df_deathcity_ind = (
        df_deathcity_ind.groupby("wiki_id")["deathcity_model"].apply(list).reset_index()
    )

    dict_deathcity_individual = df_deathcity_ind[
        ["wiki_id", "deathcity_model"]
    ].to_dict(orient="records")

    dict_deathcity_individual = {
        x["wiki_id"]: x["deathcity_model"] for x in dict_deathcity_individual
    }

    final_individuals = []
    for ind in tqdm(individuals_list):
        ind.raw_deathcities = dict_deathcity_individual.get(ind.wikidata_id, None)
        final_individuals.append(ind)

    return final_individuals


def get_external_identifiers(individuals: t.List[Individual]) -> t.List[Individual]:
    df_external_id = pd.read_csv(
        WIKIDATA_RAW_DATA + "/external_identifier_individual_before_1900.csv",
        index_col=[0],
    )
    df_external_id.columns = ["wikidata_id", "name", "individual_id"]

    df_external_id["wikidata_id"] = df_external_id["wikidata_id"].apply(
        lambda x: split_wiki(x)
    )
    df_external_id = df_external_id[
        ~df_external_id["wikidata_id"].str.contains("Q")
    ].reset_index(drop=True)
    df_external_id["external_model"] = df_external_id.progress_apply(
        lambda x: ExternalID(wikidata_id=x["wikidata_id"], name=x["name"]), axis=1
    )

    df_external_id = (
        df_external_id.groupby("individual_id")["external_model"]
        .apply(list)
        .reset_index()
    )
    dict_external_id = df_external_id.to_dict(orient="records")
    dict_external_id = {
        x["individual_id"]: x["external_model"] for x in dict_external_id
    }

    new_individuals = []
    for ind in individuals:
        ind.identifiers = dict_external_id.get(ind.id.wikidata_id)
        new_individuals.append(ind)

    return new_individuals


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    import os

    CHECKPOINT_PATH = os.getenv("CHECKPOINT_PATH")

    raw_individuals = get_individual_main_wikidata_information()
    print(len(raw_individuals))
    print(raw_individuals[0])
    # save_model(raw_individuals, name=CHECKPOINT_PATH + "/raw_individuals.jsonl")
    # print("Success!")

    # individuals = load_model(Individual, name="checkpoints_dev/checkpoint_4.jsonl")
    # individuals: t.List[Individual] = get_external_identifiers(individuals)
