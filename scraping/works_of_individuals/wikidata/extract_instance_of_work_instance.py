import sys

sys.path.append("../")
import json
import os
from multiprocessing import Pool

import pandas as pd
from api import get_results
from bunka_logger import logger
from tqdm import tqdm


def create_directory_if_not_exists(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


endpoint_url = "https://query.wikidata.org/sparql"


def get_metadata(wiki_id):
    query = """
    
    SELECT ?subject ?subjectLabel ?instance ?instanceLabel

    WHERE {
        BIND(wd:%s AS ?subject)
        ?subject wdt:P31 ?instance.
  
        SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
        }
    
    """ % (
        wiki_id
    )

    return query


def final_function(wiki_id):
    try:
        results = get_results(endpoint_url, query=get_metadata(wiki_id=wiki_id))
        results = results["results"]["bindings"]
        return results
    except Exception as e:
        print(f"An error occurred for {wiki_id}: {e}")
        return None


# INDICATIVE CODE BELOW, DOES NOT WORK AT IT IS

if __name__ == "__main__":
    import sqlite3

    import pandas as pd

    # Connect to the database
    conn = sqlite3.connect("../../src/enricher/cultura_1.db")

    # Read the table into a DataFrame
    df = pd.read_sql_query("SELECT * FROM created_work", conn)
    df = df[["instance_wikidata_id", "instance_label"]].drop_duplicates()

    output_path = "../../query_to_wikidata/data"
    # output_path = "."
    list_individuals = df["instance_wikidata_id"].to_list()

    with Pool(8) as p:
        results = list(
            tqdm(p.imap(final_function, list_individuals), total=len(list_individuals))
        )

    with open(f"{output_path}/instance_of_work_instance.json", "w") as f:
        json.dump(results, f)
