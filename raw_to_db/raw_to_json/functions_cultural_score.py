import typing as t
import warnings

import pandas as pd
from bunka_logger import logger
from data_model import Individual
from sklearn import preprocessing
from sklearn.decomposition import PCA
from sys_utils import load_model, save_model

warnings.simplefilter(action="ignore", category=FutureWarning)


def get_cultural_index(individuals: t.List[Individual]) -> t.List[Individual]:
    individual_id_wikipedia_page = [
        {"wiki_id": ind.id.wikidata_id, "url": ind.wikipedia_pages}
        for ind in individuals
    ]

    df_cultural = pd.DataFrame(individual_id_wikipedia_page)
    df_cultural = df_cultural.dropna()
    df_cultural = df_cultural.explode("url").reset_index(drop=True)

    dict_wikipedia = [x.dict() for x in list(df_cultural["url"])]
    df_wikipedia = pd.DataFrame(dict_wikipedia)

    indi_wiki_wikipedia_url = [x for x in individuals if x.wikipedia_pages != None]
    indi_wiki_wikipedia_url = [
        {"wiki_id": ind.id.wikidata_id, "url": [y.url for y in ind.wikipedia_pages]}
        for ind in indi_wiki_wikipedia_url
    ]

    df_ind_url = pd.DataFrame(indi_wiki_wikipedia_url)
    df_ind_url = df_ind_url.explode("url")

    df_pca = pd.merge(df_ind_url, df_wikipedia, on="url")

    # quick fix to remove the links not correlated to languages
    df_pca["len_language"] = df_pca["language"].apply(lambda x: len(x))
    df_pca = df_pca[df_pca["len_language"] < 6].reset_index(drop=True)
    df_pca = df_pca.drop("len_language", axis=1)

    df_pca = df_pca.drop_duplicates(["wiki_id", "language"], keep="first")

    features = [
        "editors",
        "minor_edits",
        "pageviews",
        "revisions",
        "references",
        "unique_references",
        "words",
        "links_in_count",
        "links_out_count",
    ]

    top = df_pca.pivot(index="wiki_id", columns="language", values=features)

    top.columns = [
        "_".join([str(index) for index in multi_index])
        for multi_index in top.columns.ravel()
    ]
    top = top.reset_index()

    df_index = top.fillna(0)
    df_index = df_index.set_index("wiki_id")

    normalized_score = (df_index - df_index.min()) / (df_index.max() - df_index.min())
    normalized_score = normalized_score.fillna(0)

    pca = PCA(n_components=1)
    pca.fit(normalized_score)

    X_pca = pca.transform(normalized_score)

    min_max_scaler = preprocessing.MinMaxScaler(feature_range=(0.1, 1))
    X_pca_norm = min_max_scaler.fit_transform(X_pca)

    normalized_score["cultural_index"] = X_pca_norm

    final_index = (
        normalized_score["cultural_index"]
        .reset_index()
        .sort_values("cultural_index", ascending=False)
        .reset_index(drop=True)
    )

    dict_ind_score = final_index.to_dict(orient="records")
    dict_ind_score = {x["wiki_id"]: x["cultural_index"] for x in dict_ind_score}

    individuals_index = []

    for ind in individuals:
        ind.cultural_score = dict_ind_score.get(ind.id.wikidata_id)
        individuals_index.append(ind)

    return individuals_index


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    import os

    CHECKPOINT_PATH = os.getenv("CHECKPOINT_PATH")

    logger.info("Compute Cultura Index")
    individuals = load_model(Individual, name=CHECKPOINT_PATH + "/checkpoint_3.jsonl")
    individuals: t.List[Individual] = get_cultural_index(individuals)
    save_model(individuals, name=CHECKPOINT_PATH + "/checkpoint_4.jsonl")
