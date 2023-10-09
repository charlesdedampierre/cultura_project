import glob

import pandas as pd
from dotenv import load_dotenv

load_dotenv()
import os

WIKIDATA_RAW_DATA = os.getenv("WIKIDATA_RAW_DATA")


def load_sitelinks() -> pd.DataFrame:
    paths = glob.glob(WIKIDATA_RAW_DATA + "/sitelinks/*")

    data_art_sci = []
    for path in paths:
        new = pd.read_csv(path, index_col=[0])
        data_art_sci.append(new)

    data_art_sci = (
        pd.concat([x for x in data_art_sci]).drop_duplicates().reset_index(drop=True)
    )

    data_wri = pd.read_csv(WIKIDATA_RAW_DATA + "/sitelinks_writers.csv", index_col=[0])
    data_be = pd.read_csv(
        WIKIDATA_RAW_DATA + "/sitelinks_individuals_badly_extracted.csv", index_col=[0]
    )

    data_sitelinks = pd.concat([data_art_sci, data_wri, data_be])

    return data_sitelinks


def load_wikipedia_data(full_path: str) -> pd.DataFrame:
    paths = glob.glob(full_path)
    data_ori_list = []
    for path in paths:
        new = pd.read_csv(path, index_col=[0], low_memory=False)
        data_ori_list.append(new)

    data_links = pd.concat([x for x in data_ori_list]).reset_index(drop=True)

    return data_links
