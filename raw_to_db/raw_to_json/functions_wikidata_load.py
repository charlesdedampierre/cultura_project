import glob

import pandas as pd
from dotenv import load_dotenv
from utils import split_wiki

# put as an env variable


load_dotenv()
import os

WIKIDATA_RAW_DATA = os.getenv("WIKIDATA_RAW_DATA")


def load_occupation_information():
    artist_sub = pd.read_csv(
        WIKIDATA_RAW_DATA + "/artist_sub_occupations.csv", index_col=[0]
    )
    artist_sub.columns = ["item", "itemLabel"]
    artist_sub["occupation_type"] = "artist"

    science_sub = pd.read_csv(
        WIKIDATA_RAW_DATA + "/science_sub_occupations.csv", index_col=[0]
    )
    science_sub.columns = ["item", "itemLabel"]
    science_sub["occupation_type"] = "science"

    writers_sub = pd.read_csv(
        WIKIDATA_RAW_DATA + "/writer_sub_occupations.csv", index_col=[0]
    )
    writers_sub["occupation_type"] = "writer"

    occupations = pd.concat([artist_sub, science_sub, writers_sub])
    occupations.columns = ["occupation_id", "occupationLabel", "occupation_type"]
    occupations["occupation_id"] = occupations["occupation_id"].apply(
        lambda x: split_wiki(x)
    )
    occupations.columns = ["occupation_id", "occupation_name", "occupation_category"]
    return occupations


def load_nationality_location():
    nationality_coordinate = pd.read_csv(
        WIKIDATA_RAW_DATA
        + "/nationality_coordinate_new_version_with_writers_and_be.csv",
        index_col=[0],
    )
    nationality_coordinate.columns = ["location", "nationality_id"]
    nationality_coordinate = nationality_coordinate.drop_duplicates(
        "nationality_id", keep="first"
    )
    return nationality_coordinate


def load_individual_info() -> pd.DataFrame:
    paths = glob.glob(WIKIDATA_RAW_DATA + "/individual_info/*")

    list_data = []
    data_art_sci = pd.DataFrame()
    for path in paths:
        new = pd.read_csv(path, index_col=[0])
        list_data.append(new)

    data_art_sci = pd.concat([x for x in list_data])
    # data_art_sci = data_art_sci.append(new)

    data_art_sci = data_art_sci.drop_duplicates().reset_index(drop=True)
    data_wri = pd.read_csv(
        WIKIDATA_RAW_DATA + "/individuals_writers_info.csv", index_col=[0]
    )
    data_be = pd.read_csv(
        WIKIDATA_RAW_DATA + "/individuals_badly_extracted_info.csv", index_col=[0]
    )

    data = pd.concat([data_art_sci, data_wri, data_be])

    data["birthcity_id"] = data["birthcity"].apply(lambda x: split_wiki(x))
    data["nationality_id"] = data["nationality"].apply(lambda x: split_wiki(x))
    data = data.drop(["birthcity", "nationality"], 1)

    return data


def load_individual_id_occupation_id() -> pd.DataFrame:
    artists = pd.read_csv(WIKIDATA_RAW_DATA + "/artists.csv", index_col=[0])
    scientists = pd.read_csv(WIKIDATA_RAW_DATA + "/scientists.csv", index_col=[0])
    writers = pd.read_csv(WIKIDATA_RAW_DATA + "/writers.csv", index_col=[0])

    be_1 = pd.read_csv(
        WIKIDATA_RAW_DATA + "/individuals_badly_extracted.csv", index_col=[0]
    )
    be_2 = pd.read_csv(
        WIKIDATA_RAW_DATA + "/individuals_badly_extracted_2.csv", index_col=[0]
    )
    be_3 = pd.read_csv(
        WIKIDATA_RAW_DATA + "/individuals_badly_extracted_3.csv", index_col=[0]
    )

    be = pd.concat([be_1, be_2, be_3])
    be = be.drop_duplicates()

    artists.columns = ["item", "itemLabel", "occupation"]
    scientists.columns = ["item", "itemLabel", "occupation"]

    data = pd.concat([artists, scientists, writers, be])
    data["individual_id"] = data["item"].apply(lambda x: split_wiki(x))
    data = data.drop("item", 1)
    data.columns = ["individual_name", "occupation_id", "individual_id"]

    return data


def load_deathcity():
    df_deathcity_ind = pd.read_csv(
        WIKIDATA_RAW_DATA + "/individuals_deathcity.csv", index_col=[0]
    )
    df_deathcity_ind = df_deathcity_ind[
        ["wiki_id", "deathcity", "deathcityLabel"]
    ].dropna()
    df_deathcity_ind["deathcity"] = df_deathcity_ind["deathcity"].apply(
        lambda x: split_wiki(x)
    )
    df_deathcity_ind = df_deathcity_ind.reset_index(drop=True)
    df_deathcity = df_deathcity_ind[["deathcity", "deathcityLabel"]].drop_duplicates()
    df_deathcity.columns = ["wikidata_id", "name"]

    df_deathcity_location = pd.read_csv(
        WIKIDATA_RAW_DATA + "/deathcity_location.csv", index_col=[0]
    )
    df_deathcity_location.columns = [
        "wikidata_id",
        "country_wikidata_id",
        "contry_name",
        "location",
    ]
    df_deathcity_location["country_wikidata_id"] = df_deathcity_location[
        "country_wikidata_id"
    ].apply(lambda x: split_wiki(x))
    df_deathcity_location = df_deathcity_location.dropna()

    final_deathcity = pd.merge(
        df_deathcity_location, df_deathcity, on="wikidata_id", how="outer"
    )
    final_deathcity = final_deathcity[~final_deathcity["location"].isna()]
    df_deathcity_ind = df_deathcity_ind.dropna()

    # final_deathcity = final_deathcity.drop_duplicates("wikidata_id", keep="first")
    return df_deathcity_ind, final_deathcity


def load_birthcity_country():
    data_art_sci = pd.read_csv(
        WIKIDATA_RAW_DATA + "/country_from_birthcity.csv", index_col=[0]
    )
    data_wri = pd.read_csv(
        WIKIDATA_RAW_DATA + "/country_from_birthcity_writers.csv", index_col=[0]
    )
    data_be = pd.read_csv(
        WIKIDATA_RAW_DATA + "/country_from_birthcity_badly_extracted.csv", index_col=[0]
    )

    data_birthcity_country = pd.concat(
        [data_art_sci, data_wri, data_be]
    ).drop_duplicates()
    data_birthcity_country = data_birthcity_country.sort_values(
        ["birthcity_wiki_id", "location"]
    )
    data_birthcity_country = data_birthcity_country.drop_duplicates(
        "birthcity_wiki_id", keep="first"
    ).reset_index(drop=True)
    data_birthcity_country["country_wikidata_id"] = data_birthcity_country[
        "country"
    ].apply(lambda x: split_wiki(x))

    data_birthcity_country = data_birthcity_country[
        ["countryLabel", "location", "birthcity_wiki_id", "country_wikidata_id"]
    ]
    data_birthcity_country = data_birthcity_country.rename(
        columns={"birthcity_wiki_id": "birthcity_id"}
    )

    country_coordinate = pd.read_csv(
        WIKIDATA_RAW_DATA + "/country_coordinate_new_version_with_writers_and_be.csv",
        index_col=[0],
    )
    country_coordinate.columns = ["country_location", "country_wikidata_id"]
    data_birthcity_country = pd.merge(
        data_birthcity_country, country_coordinate, on="country_wikidata_id"
    )

    return data_birthcity_country
