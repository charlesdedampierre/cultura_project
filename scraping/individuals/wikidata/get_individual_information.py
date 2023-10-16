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
    """individuals = pd.read_csv("data/artists_scientists.csv", index_col=[0])
    individuals["wiki_id"] = individuals["item"].apply(
        lambda x: x.split("www.wikidata.org/entity/")[1]
    )

    # Deduplicate
    all_individuals = list(set(individuals["wiki_id"].to_list()))

    n = 100000  # Chunks of 100000 inviduals
    all_individuals_chunks = [
        all_individuals[i : i + n] for i in range(0, len(all_individuals), n)
    ]
    all_individuals_chunks = all_individuals_chunks[12:]"""

    import pickle

    with open("data/old_info/rest_wiki_to_do.pickle", "rb") as handle:
        all_individuals_chunks_rest = pickle.load(handle)

    all_individuals_chunks_rest = list(all_individuals_chunks_rest)

    with Pool(9) as p:
        res = list(
            tqdm(
                p.imap(get_info, all_individuals_chunks_rest),
                total=len(all_individuals_chunks_rest),
            )
        )

    final = pd.concat([art for art in res])
    final = final.reset_index(drop=True)
    final.to_csv(f"data/info/individuals_info_chunk_rest.csv")

    """ count = 0
    for individuals in all_individuals_chunks:
        print(count)
        with Pool(9) as p:
            res = list(tqdm(p.imap(get_info, individuals), total=len(individuals)))

        final = pd.concat([art for art in res])
        final = final.reset_index(drop=True)
        final.to_csv(f"data/info/individuals_info_chunk_{count}.csv")
        count += 1
    """
