from multiprocessing import Pool

import pandas as pd
from tqdm import tqdm
from wikidata_extract import WikidataApi


def get_info(wiki_id):
    query = """SELECT ?genderLabel ?birthdateLabel ?nationality ?nationalityLabel ?birthcity ?birthcityLabel

    WHERE {
    
    OPTIONAL { wd:%s wdt:P21 ?gender. }
    OPTIONAL { wd:%s wdt:P569 ?birthdate. }        
    OPTIONAL { wd:%s wdt:P27 ?nationality. }
    OPTIONAL { wd:%s wdt:P570 ?deathdate. }
    OPTIONAL { wd:%s wdt:P19 ?birthcity. }
    OPTIONAL { wd:%s wdt:P20 ?deathcity. }

    SERVICE wikibase:label { bd:serviceParam wikibase:language 'en'. }

    }
    """ % (
        wiki_id,
        wiki_id,
        wiki_id,
        wiki_id,
        wiki_id,
        wiki_id,
    )

    try:
        res = WikidataApi(query)
        res["wiki_id"] = wiki_id
    except:
        res = None

    return res


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


# INDICATIVE CODE BELOW, DOES NOT WORK AT IT IS

if __name__ == "__main__":
    writers_uniques = pd.read_csv("data/writers_dedoublons.csv")
    all_writers = list(set(writers_uniques["wiki_id"].to_list()))

    with Pool(9) as p:
        res = list(
            tqdm(
                p.imap(get_info, all_writers),
                total=len(all_writers),
            )
        )

    final = pd.concat([art for art in res])
    final = final.reset_index(drop=True)
    final.to_csv(f"data/individuals_writers_info.csv")
