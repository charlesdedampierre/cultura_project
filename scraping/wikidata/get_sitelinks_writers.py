from wikidata_extract import WikidataApi
import pandas as pd
from multiprocessing import Pool
from tqdm import tqdm
import pickle


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


if __name__ == "__main__":
    writers_uniques = pd.read_csv("data/writers_dedoublons.csv")
    all_writers = list(set(writers_uniques["wiki_id"].to_list()))

    with Pool(9) as p:
        res = list(tqdm(p.imap(get_sitelinks, all_writers), total=len(all_writers)))

    final = pd.concat([art for art in res])
    final = final.reset_index(drop=True)
    final.to_csv(f"data/sitelinks_writers.csv")
