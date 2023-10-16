import sys

sys.path.append("../")
import glob
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
    query = """SELECT  ?subject ?subjectLabel
            ?instance ?instanceLabel
        ?subclass ?subclassLabel
        ?inception
        ?time_period ?time_periodLabel
        ?culture ?cultureLabel 
        ?architecture_style ?architecture_styleLabel 
        ?founded_by ?founded_byLabel 
        ?creator ?creatorLabel
        ?country ?countryLabel
        ?territory ?territoryLabel
        ?genre ?genreLabel
        ?movement ?movementLabel
        
    WHERE {
    BIND(wd:%s AS ?subject)
    OPTIONAL { ?subject wdt:P31 ?instance.}
    OPTIONAL { ?subject wdt:P279 ?subclass.}
    OPTIONAL { ?subject wdt:P571 ?inception. }
    OPTIONAL { ?subject wdt:P2348 ?time_period. }
    OPTIONAL { ?subject wdt:P2596 ?culture. }
    OPTIONAL {?subject wdt:P149 ?architecture_style. }
    OPTIONAL { ?subject wdt:P112 ?founded_by. }
    OPTIONAL { ?subject wdt:P170 ?creator. }
    OPTIONAL { ?subject wdt:P17 ?country. }
    OPTIONAL { ?subject wdt:P131 ?territory. }
    OPTIONAL { ?subject wdt:P136 ?genre. }
    OPTIONAL { ?subject wdt:P135 ?movement. }
    
    SERVICE wikibase:label {
        bd:serviceParam wikibase:language "en".

    }
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
    except:
        return None


# INDICATIVE CODE BELOW, DOES NOT WORK AT IT IS

if __name__ == "__main__":
    input_paths = glob.glob("../raw_data/complex_objects/*")
    input_path = input_paths[1]

    # name = input_path.split('complex_objects/')[1]
    output_path = "../raw_data/raw_metadata"
    # create_directory_if_not_exists()

    logger.info("Load Data")
    # Open the JSON file and read its contents
    with open(input_path) as f:
        data = f.read()

    # Parse the JSON data into a dictionary
    dict_data = json.loads(data)

    # Batch the data

    batch_size = 100000
    total_rows = len(dict_data)
    num_batches = total_rows // batch_size + (total_rows % batch_size != 0)

    for i in tqdm(range(num_batches)[33:]):
        start_index = i * batch_size
        end_index = min((i + 1) * batch_size, total_rows)

        batch_wiki_ids = [
            row["item"]["value"].split("entity/")[1]
            for row in dict_data[start_index:end_index]
        ]
        final_list = []

        with Pool(8) as p:
            results = list(
                tqdm(p.imap(final_function, batch_wiki_ids), total=len(batch_wiki_ids))
            )
            final_list.append(results)

        logger.info(f"Save Data Batch {i + 1}")

        """with open(f"../raw_data/raw_metadata/work_of_art/batch_{i + 1}.json", "w") as f:
            json.dump(final_list[0], f)"""
