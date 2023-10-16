from multiprocessing import Pool

import pandas as pd
import requests
from tqdm import tqdm


def get_VIAF_information(id=160302178):
    url = f"http://viaf.org/viaf/{id}/viaf.json"
    # Send an HTTP request to the VIAF API
    response = requests.get(url)
    data_json = response.json()

    return data_json


def get_work(data_json):
    list_of_works = [x["title"] for x in data_json["titles"]["work"]]
    list_of_ids = [x.get("@id", None) for x in data_json["titles"]["work"]]
    df = pd.DataFrame({"title": list_of_works, "viaf_ids": list_of_ids})
    return df


data_json = get_VIAF_information(id=160302178)
df = get_work(data_json)

# INDICATIVE CODE BELOW, DOES NOT WORK AT IT IS

if __name__ == "__main__":
    with Pool(8) as p:
        results = list(
            tqdm(
                p.imap(get_VIAF_information, list_individuals),
                total=len(list_individuals),
            )
        )
