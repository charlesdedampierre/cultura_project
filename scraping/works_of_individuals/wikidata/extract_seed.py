import json

from api import get_results

endpoint_url = "https://query.wikidata.org/sparql"


def get_items(wiki_id):
    # Count entities
    query = """
    SELECT ?item
    WHERE {
    VALUES ?targetClass { wd:%s }
    ?item wdt:P31/wdt:P279* ?targetClass.}
        """ % (
        wiki_id
    )

    return query


raw_seeds = [
    {"wiki_id": "Q811979", "wiki_label": "architectural_structure"},
    {"wiki_id": "Q838948", "wiki_label": "work_of_art"},
    {"wiki_id": "Q39546", "wiki_label": "tool"},
    {"wiki_id": "Q839954", "wiki_label": "archaeological_site"},
    {"wiki_id": "Q121359", "wiki_label": "infrastructure"},
]

# INDICATIVE CODE BELOW, DOES NOT WORK AT IT IS

if __name__ == "__main__":
    path = "../raw_data/complex_objects"

    for seed in raw_seeds:
        if seed["wiki_id"] == "Q811979":
            continue
        elif seed["wiki_id"] == "Q39546":
            continue
        else:
            print(seed)
            results = get_results(
                endpoint_url, query=get_items(wiki_id=seed["wiki_id"])
            )
            with open(f"{path}/raw_{seed['wiki_label']}.json", "w") as f:
                json.dump(results["results"]["bindings"], f)
