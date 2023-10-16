import pickle
import sqlite3
from multiprocessing import Pool

import pandas as pd
import requests
from tqdm import tqdm

# Page have been filtered as the following: writers, artists and scientist
# Impact_year = birthdate + 35 ans
# birthdate_filtered = birthdate[birthdate['impact_year']<=1900]


def get_page_info(info):
    type = "links"

    link = info[0]
    wiki = info[1]
    page_name = info[2]
    try:
        # types:
        # - articleinfo
        # - links
        # - prose

        query = f"https://xtools.wmflabs.org/api/page/{type}/{wiki}.wikipedia.org/{page_name}"

        res_dict = {}
        res = requests.get(query).json()
        res_dict[link] = res

    except:
        res_dict = None

    return res_dict


def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i : i + n]


# INDICATIVE CODE BELOW, DOES NOT WORK AT IT IS

if __name__ == "__main__":
    conn = sqlite3.connect("../cultura.db")
    data = pd.read_sql_query("SELECT * FROM sitelinks_impact_year_before_1900", conn)

    # How many elements each
    # list should have

    """lisf_df = list(divide_chunks(data, 100000))

    with open("data/list_saved.pickle", "wb") as handle:
        pickle.dump(lisf_df, handle, protocol=pickle.HIGHEST_PROTOCOL)"""

    with open("data/list_saved.pickle", "rb") as handle:
        lisf_df = pickle.load(handle)

    # lisf_df = [lisf_df]

    count = 0
    for wikipedia in lisf_df:
        # wikipedia = wikipedia.sample(10, random_state=42)
        print(count)
        wikipedia["page_name"] = wikipedia["sitelinks"].apply(
            lambda x: x.split("/wiki/")[1]
        )

        # Tranform necessary information
        sitelinks = wikipedia["sitelinks"].to_list()
        wikis = wikipedia["wiki_nat"].to_list()
        page_names = wikipedia["page_name"].to_list()

        infos = zip(sitelinks, wikis, page_names)

        with Pool(8) as p:
            res_total = list(tqdm(p.imap(get_page_info, infos), total=len(wikipedia)))

        fin = [pd.DataFrame(x).T for x in res_total]
        fin_res = pd.concat([x for x in fin])
        df_res = fin_res.reset_index()
        df_res = df_res.rename(columns={"index": "sitelinks"})

        df_res.to_csv(f"data/links/df_impact_year_inferior_1900_{count}.csv")
        count += 1
