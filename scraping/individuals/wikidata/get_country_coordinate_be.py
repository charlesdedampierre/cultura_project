from multiprocessing import Pool

import pandas as pd
from tqdm import tqdm
from wikidata_extract import WikidataApi


def get_coordinate(wiki_id):
    try:
        query = """Select ?item
        WHERE {

        wd:%s wdt:P625 ?item.
        
        SERVICE wikibase:label { bd:serviceParam wikibase:language 'en'. }
        
        }""" % (
            wiki_id
        )

        res = WikidataApi(query)
        res["country_id"] = wiki_id
    except:
        res = None

    return res


# INDICATIVE CODE BELOW, DOES NOT WORK AT IT IS

if __name__ == "__main__":
    import sqlite3

    conn = sqlite3.connect("../cultura.db")

    region = pd.read_sql_query("SELECT * FROM birthcity_information", conn)
    region = region[["countryLabel", "country_id"]].drop_duplicates()

    countries = region["country_id"].to_list()

    with Pool(8) as p:
        res = list(tqdm(p.imap(get_coordinate, countries), total=len(countries)))

    final = pd.concat([art for art in res])
    final = final.reset_index(drop=True)
    final.to_csv("data/country_coordinate_new_version_with_writers_and_be.csv")
