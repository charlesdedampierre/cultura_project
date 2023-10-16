from multiprocessing import Pool

import pandas as pd
from tqdm import tqdm
from wikidata_extract import WikidataApi


def get_country(wiki_id):
    query = """ SELECT  ?country ?countryLabel ?location ?continent ?continentLabel

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
        res["birthcity_wiki_id"] = wiki_id
    except:
        res = None

    return res


# INDICATIVE CODE BELOW, DOES NOT WORK AT IT IS

if __name__ == "__main__":
    data = pd.read_csv("data/individuals_badly_extracted_info.csv")
    data = data[data["birthcity"].notna()]

    no_found_url = "http://www.wikidata.org/.well-known/genid"
    data = data[~data["birthcity"].str.contains(no_found_url)]

    data["birthcity"] = data["birthcity"].apply(
        lambda x: x.split("www.wikidata.org/entity/")[1]
    )

    cities = list(set(data["birthcity"].to_list()))

    with Pool(9) as p:
        res = list(tqdm(p.imap(get_country, cities), total=len(cities)))

    final = pd.concat([art for art in res])
    final = final.reset_index(drop=True)
    final.to_csv(f"data/country_from_birthcity_badly_extracted.csv")
