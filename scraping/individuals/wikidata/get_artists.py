from multiprocessing import Pool

import pandas as pd
from tqdm import tqdm
from wikidata_extract import WikidataApi

# Get all individuals whose occupation is wd:Q266569
query = """Select ?item ?itemLabel
WHERE {
  
  ?item wdt:P106 wd:Q266569
   
  SERVICE wikibase:label { bd:serviceParam wikibase:language 'en'. }
  
  }"""


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
        res.columns = ["item", "item_name"]
        res["occupation"] = wiki_id
    except:
        res = None

    return res


"""df_art = []
for occupation in tqdm(all_occupations, total=len(all_occupations)):
    res = get_individuals(occupation)
    df_art.append(res)

final = pd.concat([art for art in df_art])

"""
# INDICATIVE CODE BELOW, DOES NOT WORK AT IT IS

if __name__ == "__main__":
    artist_occupations = pd.read_csv("data/artist_sub_occupations.csv")
    artist_occupations["wiki_id"] = artist_occupations["item"].apply(
        lambda x: x.split("www.wikidata.org/entity/")[1]
    )
    all_occupations = artist_occupations["wiki_id"].to_list()
    with Pool(8) as p:
        res = list(
            tqdm(p.imap(get_individuals, all_occupations), total=len(all_occupations))
        )

    final = pd.concat([art for art in res])
    final.to_csv("data/artists.csv")
