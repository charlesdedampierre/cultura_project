import sqlite3
from multiprocessing import Pool

import numpy as np
import pandas as pd
from tqdm import tqdm
from wikidata_extract import WikidataApi

# The goal is to get rid of anybody that is not human


def get_individuals(wiki_id):
    try:
        query = """Select ?instance ?instanceLabel

        WHERE {

        wd:%s wdt:P31 ?instance

        SERVICE wikibase:label { bd:serviceParam wikibase:language 'en'. }}
        """ % (
            wiki_id
        )

        res = WikidataApi(query)
        # res.columns = ["item", "item_name"]
        res["individual_id"] = wiki_id
    except:
        res = None
    return res


# INDICATIVE CODE BELOW, DOES NOT WORK AT IT IS

if __name__ == "__main__":
    # Load Database
    conn = sqlite3.connect("cultura.db")
    individuals = pd.read_sql_query("SELECT * FROM individuals", conn)
    # individuals = individuals.sample(10, random_state=42)
    individuals = individuals[["individual_id"]].drop_duplicates()
    individuals = individuals.sample(100, random_state=42)

    list_df = np.array_split(individuals, 20)

    count = 0
    for chunk in list_df:
        indivuals_id = chunk["individual_id"].to_list()
        # indivuals_id = list(set(individuals["individual_id"]))

        with Pool(8) as p:
            res = list(
                tqdm(p.imap(get_individuals, indivuals_id), total=len(indivuals_id))
            )

        final = pd.concat([art for art in res])
        final.to_csv(f"query_to_wikidata/data/individual_instances/{count}.csv")
        count += 1
        print(final)
