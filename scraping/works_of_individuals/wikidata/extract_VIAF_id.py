import sys

sys.path.append("../")
import json
import sqlite3
from multiprocessing import Pool

import pandas as pd
import requests
from bunka_logger import logger
from more_itertools import chunked
from tqdm import tqdm


def get_VIAF_information(id=160302178):
    try:
        url = f"http://viaf.org/viaf/{id}/viaf.json"
        # Send an HTTP request to the VIAF API
        response = requests.get(url)
        data_json = response.json()
        data_json["origin_id"] = id
        return data_json

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


"""def get_work(data_json):
    list_of_works = [x['title'] for x in data_json['titles']['work']]
    list_of_ids= [x.get('@id', None) for x in data_json['titles']['work'] ]
    df = pd.DataFrame({'title':list_of_works, 'viaf_ids':list_of_ids})
    return df
"""

# INDICATIVE CODE BELOW, DOES NOT WORK AT IT IS

if __name__ == "__main__":
    # Connect to the database
    conn = sqlite3.connect("../../src/enricher/cultura_1.db")

    # Read the table into a DataFrame
    df = pd.read_sql_query("SELECT * FROM individual_viaf_id", conn)
    # df = df.sample(100, random_state=42)

    output_path = "../../query_to_viaf"
    # output_path = "."
    list_ids = list(set(df["viaf_id"]))
    batched_ids = list(chunked(list_ids, 10))

    for i, chunk in enumerate(batched_ids):
        with Pool(8) as p:
            results = list(tqdm(p.imap(get_VIAF_information, chunk), total=len(chunk)))

        with open(f"{output_path}/viaf_information_chunk_{i}.json", "w") as f:
            json.dump(results, f)

""" with open(f"{output_path}/viaf_information.json", "w") as f:
        json.dump(results, f)
"""
