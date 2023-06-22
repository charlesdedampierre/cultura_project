import sys

sys.path.append("../")

import json
from api import get_results
import pandas as pd
from multiprocessing import Pool
from tqdm import tqdm
import os
import sqlite3
from more_itertools import chunked


def get_metadata(wiki_id):
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

    return query


endpoint_url = "https://query.wikidata.org/sparql"


def final_function(wiki_id):
    try:
        results = get_results(endpoint_url, query=get_metadata(wiki_id=wiki_id))
        results = results["results"]["bindings"]
        return results
    except Exception as e:
        print(f"An error occurred for {wiki_id}: {e}")
        return None


if __name__ == "__main__":
    # Connect to the database
    conn = sqlite3.connect("../../src/enricher/cultura_1.db")

    df_instance = pd.read_sql_query("SELECT * FROM created_work", conn)
    list_objects = df_instance["work_wikidata_id"].unique().tolist()
    print(list_objects[0])
    print(len(list_objects))

    output_path = "../../query_to_wikidata/data"

    batched_ids = list(chunked(list_objects, 100000))
    batched_ids.sort()

    for i, chunk in enumerate(batched_ids):
        with Pool(8) as p:
            results = list(tqdm(p.imap(final_function, chunk), total=len(chunk)))

        with open(f"{output_path}/objects_identifiers_chunk_{i}.json", "w") as f:
            json.dump(results, f)
