import sqlite3
from multiprocessing import Pool

import pandas as pd
from tqdm import tqdm
from wikidata_extract import WikidataApi


def get_info(wiki_id):
    query = """SELECT (YEAR(?deathdate) AS ?deathyear)

    WHERE {
        OPTIONAL { wd:%s wdt:P570 ?deathdate. }
       
    
        SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
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


# INDICATIVE CODE BELOW, DOES NOT WORK AT IT IS
if __name__ == "__main__":
    conn = sqlite3.connect("../../../cultura.db")

    # Get wikipedia
    data = pd.read_sql_query("SELECT * FROM individuals_main_information", conn)
    # data = data.sample(1000, random_state=42)
    all_individuals = data["individual_wikidata_id"].to_list()

    with Pool(9) as p:
        res = list(tqdm(p.imap(get_info, all_individuals), total=len(all_individuals)))

    final = pd.concat([art for art in res])
    final = final.reset_index(drop=True)
    print(final)
    final.to_csv(f"../../../raw_data/wikidata_data/deathyear.csv")
