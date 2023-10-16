import sqlite3
from multiprocessing import Pool

import pandas as pd
from tqdm import tqdm
from wikidata_extract import WikidataApi


def get_database_id(wiki_id):
    query = """
    
    SELECT 
  ?p ?pLabel
    WHERE
    {
        BIND( wd:%s as ?comp2)
        { 
            ?comp2 ?wdt ?v . 
            ?p wikibase:directClaim ?wdt ; wikibase:propertyType wikibase:ExternalId .
        
        }
        UNION { BIND(wd:%s as ?p) }
    SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". } 
    }
        
        
    
    """ % (
        wiki_id,
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
    conn = sqlite3.connect("../cultura.db")

    # Get wikipedia
    data = pd.read_sql_query(
        "SELECT * FROM cultural_index_impact_year_before_1900", conn
    )
    all_individuals = data["individual_id"].to_list()

    with Pool(9) as p:
        res = list(
            tqdm(p.imap(get_database_id, all_individuals), total=len(all_individuals))
        )

    print(res)
    final = pd.concat([art for art in res])
    final = final.reset_index(drop=True)
    final.to_csv(f"data/external_identifier_individual_before_1900.csv")
    print(final)
