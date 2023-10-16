import pickle
from multiprocessing import Pool

import pandas as pd
from tqdm import tqdm
from wikidata_extract import WikidataApi


def get_sitelinks(wiki_id):
    query = """SELECT ?sitelinks


            WHERE {
                
        ?sitelinks schema:about wd:%s.

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
    """individuals = pd.read_csv("data/artists_scientists.csv", index_col=[0])
    individuals["wiki_id"] = individuals["item"].apply(
        lambda x: x.split("www.wikidata.org/entity/")[1]
    )

    all_individuals = list(set(individuals["wiki_id"].to_list()))"""

    with open("data/all_individuals_chunks.pickle", "rb") as handle:
        all_individuals_chunks = pickle.load(handle)

    all_individuals_chunks = list(all_individuals_chunks)[5:]

    count = 5
    for chunk in all_individuals_chunks:
        print(count)
        with Pool(9) as p:
            res = list(tqdm(p.imap(get_sitelinks, chunk), total=len(chunk)))

        final = pd.concat([art for art in res])
        final = final.reset_index(drop=True)
        final.to_csv(f"data/sitelinks/individuals_sitelinks_{count}.csv")
        count += 1
