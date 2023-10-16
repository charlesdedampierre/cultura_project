import sys
from multiprocessing import Pool

import pandas as pd
from SPARQLWrapper import JSON, SPARQLWrapper
from tqdm import tqdm


def get_results(query):
    endpoint_url = "https://query.wikidata.org/sparql"
    user_agent = "WDQS-example Python/%s.%s" % (
        sys.version_info[0],
        sys.version_info[1],
    )
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()


def get_feature(wikidata_id, feature_id="P279", language="en"):
    text = """
        SELECT ?featureLabel

    WHERE {
        
    wd:%s wdt:%s ?feature.
    
    SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],%s". }

    }

    """ % (
        wikidata_id,
        feature_id,
        language,
    )

    return text


def WikidataApi(query: str) -> pd.DataFrame:
    """Wikidata Wrapper. Add a query in Sparql and outputs a DataFrame format"""

    json_res = get_results(query)
    data = pd.json_normalize(json_res["results"]["bindings"])

    # Filter the column
    data = data.filter(like=".value", axis=1)
    data.columns = data.columns.str.replace(".value", "", regex=True)

    # Erase the 'Label' at the end of columns
    # data.columns = data.columns.str.replace("Label", "", regex=True)
    return data


def get_feature_func(wikidata_id: str = "Q5123331") -> str:
    """Get the feature (the first one in the list) of a wikidata_id
    based on wikidata api. It returns a string with the feature.

    for instance: P279 for the subclass. P31 for the instance etc

    """
    try:
        # Get instance is the SPARQL query
        query = get_feature(wikidata_id=wikidata_id, feature_id="P106")
        res = WikidataApi(query)
        res = list(res["feature"])
    except:
        res = None

    return {"wiki_id": wikidata_id, "occupations": res}


# INDICATIVE CODE BELOW, DOES NOT WORK AT IT IS

if __name__ == "__main__":
    data = pd.read_csv("data/wikidata.csv", index_col=[0], low_memory=False)
    # data = data.sample(1000)
    data["wiki_number"] = data["item"].apply(
        lambda x: x.split("www.wikidata.org/wiki/")[1]
    )

    items = data["wiki_number"].to_list()
    items = list(set(items))

    with Pool(8) as p:
        res = list(tqdm(p.imap(get_feature_func, items), total=len(items)))

    result = pd.DataFrame(res)
    result.to_csv("test_occupation.csv")
