from multiprocessing import Pool

import pandas as pd
from tqdm import tqdm
from wikidata_extract import WikidataApi


def get_info_2(wiki_id):
    query = """
    SELECT ?deathcity ?deathcityLabel ?deathcity_coordinates ?modern_country ?modern_countryLabel

    WHERE {
        OPTIONAL { wd:%s wdt:P20 ?deathcity. }
        OPTIONAL { ?deathcity wdt:P625 ?deathcity_coordinates. }
        OPTIONAL { ?deathcity wdt:P17 ?modern_country. }

        SERVICE wikibase:label { bd:serviceParam wikibase:language 'en'. }
    }
    """ % (
        wiki_id,
    )

    try:
        res = WikidataApi(query)
        res["wiki_id"] = wiki_id
    except:
        res = None

    return res


def get_info(wiki_id):
    query = """
    SELECT ?deathcity ?deathcityLabel ?deathdate

    WHERE {
        OPTIONAL { wd:%s wdt:P20 ?deathcity. }
        OPTIONAL { wd:%s wdt:P570 ?deathdate. }

    
        SERVICE wikibase:label { bd:serviceParam wikibase:language 'en'. }
    }
    """ % (
        wiki_id,
        wiki_id,
    )

    try:
        res = WikidataApi(query)
        res["wiki_id"] = wiki_id
    except:
        res = None

    return res


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


# INDICATIVE CODE BELOW, DOES NOT WORK AT IT IS

if __name__ == "__main__":
    import sqlite3
    import sys

    sys.path.append("../../../")
    from functions_env import DB_PATH

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    df_individuals = pd.read_sql_query(
        "SELECT * FROM individuals_main_information", conn
    )

    list_indiviudals = df_individuals.individual_wikidata_id.unique()
    # list_indiviudals = list_indiviudals[:20]

    with Pool(7) as p:
        res = list(
            tqdm(
                p.imap(get_info, list_indiviudals),
                total=len(list_indiviudals),
            )
        )

    final = pd.concat([art for art in res])
    final = final.reset_index(drop=True)

    data_path = "../../../raw_data/wikidata_data/individuals_deathcity.csv"

    final.to_csv(data_path)

    print(final)
    """
    with open("data/old_info/rest_wiki_to_do.pickle", "rb") as handle:
        all_individuals_chunks_rest = pickle.load(handle)

    all_individuals_chunks_rest = list(all_individuals_chunks_rest)

    with Pool(9) as p:
        res = list(
            tqdm(
                p.imap(get_info, all_individuals_chunks_rest),
                total=len(all_individuals_chunks_rest),
            )
        )

    final = pd.concat([art for art in res])
    final = final.reset_index(drop=True)
    final.to_csv(f"data/info/individuals_info_chunk_rest.csv")

    """
