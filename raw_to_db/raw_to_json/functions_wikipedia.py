import os
import typing as t

import pandas as pd
from data_model import Individual, WikipediaPage
from functions_wikipedia_load import load_sitelinks, load_wikipedia_data
from sys_utils import load_model
from tqdm import tqdm

tqdm.pandas()
from bunka_logger import logger
from sys_utils import save_model

WIKIPEDIA_RAW_DATA = os.getenv("WIKIPEDIA_RAW_DATA")


def get_wikipedia_information(individuals: t.List[Individual]) -> t.List[Individual]:
    data_sitelinks = load_sitelinks()
    individual_wiki_id = [x.id.wikidata_id for x in individuals]

    data_sitelinks = data_sitelinks[
        data_sitelinks["wiki_id"].isin(individual_wiki_id)
    ].reset_index(drop=True)

    data_links = load_wikipedia_data(WIKIPEDIA_RAW_DATA + "/links/*")
    data_prose = load_wikipedia_data(WIKIPEDIA_RAW_DATA + "/prose/*")
    data_info = load_wikipedia_data(WIKIPEDIA_RAW_DATA + "/article_info/*")

    data_wikipedia = pd.merge(data_sitelinks, data_links, on="sitelinks", how="outer")
    data_wikipedia = pd.merge(data_prose, data_wikipedia, on="sitelinks", how="outer")
    data_wikipedia = pd.merge(data_info, data_wikipedia, on="sitelinks", how="outer")

    data_wikipedia["language"] = data_wikipedia["sitelinks"].apply(
        lambda x: x.split("https://")[1].split(".wikipedia.org")[0]
    )

    df_sites = data_wikipedia[
        [
            "sitelinks",
            "editors",
            "minor_edits",
            "author",
            "author_editcount",
            "pageviews",
            "revisions",
            "references",
            "unique_references",
            "words",
            "characters",
            "links_ext_count",
            "links_in_count",
            "links_out_count",
            "language",
            "created_at",
        ]
    ].copy()

    df_sites = df_sites.rename(columns={"sitelinks": "url"})
    df_sites = df_sites.drop_duplicates("url", keep="first")

    wikipedia_pages = []
    for x in tqdm(df_sites.to_dict(orient="records")):
        res = {key: None if value != value else value for key, value in x.items()}
        page = WikipediaPage(**res)
        wikipedia_pages.append(page)

    wikipedia_url_wikipedia_model = {x.url: x for x in wikipedia_pages}
    data_sitelinks["wikipedia_model"] = data_sitelinks["sitelinks"].progress_apply(
        lambda x: wikipedia_url_wikipedia_model.get(x)
    )

    # the sitelinks are for the whole dataset. We are only working on people borth untuil 1850
    data_sitelinks = data_sitelinks.dropna().reset_index(drop=True)
    data_sitelinks = (
        data_sitelinks.groupby("wiki_id")["wikipedia_model"].apply(list).reset_index()
    )

    dict_data_sitelinks = data_sitelinks.to_dict(orient="records")
    dict_data_sitelinks = {
        x["wiki_id"]: x["wikipedia_model"] for x in dict_data_sitelinks
    }

    new_individuals = []
    for ind in individuals:
        ind.wikipedia_pages = dict_data_sitelinks.get(ind.id.wikidata_id)
        new_individuals.append(ind)

    return new_individuals


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    CHECKPOINT_PATH = os.getenv("CHECKPOINT_PATH")

    individuals: t.List[Individual] = load_model(
        Individual, name=CHECKPOINT_PATH + "/checkpoint_2.jsonl"
    )

    logger.info("Add Wikipedia Information")
    new_individuals: t.List[Individual] = get_wikipedia_information(individuals)
    logger.info("Save Model")
    save_model(individuals, name=CHECKPOINT_PATH + "/checkpoint_3.jsonl")
