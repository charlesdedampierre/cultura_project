from multiprocessing import Pool

import pandas as pd
from tqdm import tqdm
from wikidata_extract import WikidataApi


def get_info(wiki_id):
    query = """
                SELECT ?translated_name ?lang
                WHERE {
                wd:%s rdfs:label ?translated_name.
                BIND(LANG(?translated_name) AS ?lang)
                }

    """ % (
        wiki_id,
    )

    try:
        res = WikidataApi(query)
        res["wikidata_code"] = wiki_id
    except:
        res = None

    return res


# INDICATIVE CODE BELOW, DOES NOT WORK AT IT IS

if __name__ == "__main__":
    all_individuals = ["Q15031"]

    data = pd.read_csv("/Users/charlesdedampierre/Downloads/namecode.csv")
    all_individuals = list(data.wikidata_code)
    all_individuals = list(set(all_individuals))
    import random

    # all_individuals = random.sample(all_individuals, 100)

    with Pool(9) as p:
        res = list(
            tqdm(
                p.imap(get_info, all_individuals),
                total=len(all_individuals),
            )
        )

    final = pd.concat([art for art in res])
    final = final.reset_index(drop=True)
    final.to_csv("translated_names.csv")

    print(final)
