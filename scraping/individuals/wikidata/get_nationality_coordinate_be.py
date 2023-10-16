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
        res["nationality"] = wiki_id
    except:
        res = None

    return res


# INDICATIVE CODE BELOW, DOES NOT WORK AT IT IS

if __name__ == "__main__":
    import sqlite3

    conn = sqlite3.connect("../cultura.db")
    nationality = pd.read_sql_query("SELECT * FROM nationality", conn)
    nationality = nationality[["nationality_id", "nationalityLabel"]].drop_duplicates()
    nationalities = nationality["nationality_id"].to_list()

    with Pool(8) as p:
        res = list(
            tqdm(p.imap(get_coordinate, nationalities), total=len(nationalities))
        )

    final = pd.concat([art for art in res])
    final = final.reset_index(drop=True)
    final.to_csv("data/nationality_coordinate_new_version_with_writers_and_be.csv")
