from multiprocessing import Pool

import pandas as pd
from tqdm import tqdm
from wikidata_extract import WikidataApi


def get_individuals(wiki_id):
    try:
        query = """Select ?item ?itemLabel
        WHERE {
        
        ?item wdt:P106 wd:%s
        
        SERVICE wikibase:label { bd:serviceParam wikibase:language 'en'. }
        
        }""" % (
            wiki_id
        )

        res = WikidataApi(query)
        # res.columns = ["item", "item_name"]
        res["occupation"] = wiki_id
    except:
        res = None
    return res


# INDICATIVE CODE BELOW, DOES NOT WORK AT IT IS

if __name__ == "__main__":
    occupations = pd.read_csv("data/occupations_to_extract_again.csv")
    all_occupations = occupations["wiki_id"].to_list()
    with Pool(8) as p:
        res = list(
            tqdm(p.imap(get_individuals, all_occupations), total=len(all_occupations))
        )

    final = pd.concat([art for art in res])
    final.to_csv("data/individuals_badly_extracted_3.csv")
