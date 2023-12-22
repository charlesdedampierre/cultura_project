from multiprocessing import Pool

import numpy as np
import pandas as pd
from tqdm import tqdm
from wikidata_extract import WikidataApi


def split_wiki(str):
    try:
        res = str.split("www.wikidata.org/entity/")[1]
    except:
        res = np.nan
    return res


def get_country(wiki_id):
    query = """ SELECT  ?country ?countryLabel ?location

    WHERE {
        
    OPTIONAL { wd:%s wdt:P17 ?country.}
    OPTIONAL  {wd:%s wdt:P625 ?location.}
    
    SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }

    }""" % (
        wiki_id,
        wiki_id,
    )

    try:
        res = WikidataApi(query)
        res["deathcity_wiki_id"] = wiki_id
    except:
        res = None

    return res


# INDICATIVE CODE BELOW, DOES NOT WORK AT IT IS

if __name__ == "__main__":
    df_deathcity_ind = pd.read_csv(
        "../../../raw_data/wikidata_data/individuals_deathcity.csv", index_col=[0]
    )
    df_deathcity = df_deathcity_ind[["deathcity"]].dropna()
    df_deathcity["deathcity"] = df_deathcity["deathcity"].apply(lambda x: split_wiki(x))

    cities = list(set(df_deathcity["deathcity"].to_list()))

    with Pool(9) as p:
        res = list(tqdm(p.imap(get_country, cities), total=len(cities)))

    final = pd.concat([art for art in res])
    final = final.reset_index(drop=True)
    final.to_csv(f"../../../raw_data/wikidata_data/deathcity_location.csv")
