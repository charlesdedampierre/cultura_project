import numpy as np


def split_wiki(str):
    try:
        res = str.split("www.wikidata.org/entity/")[1]
    except:
        res = np.nan
    return res


def clean_date(raw_date):
    try:
        if raw_date.startswith("-"):
            clean_date = int(raw_date[:5])
        else:
            clean_date = int(raw_date[:4])

    except:
        clean_date = None
    return clean_date


def round_nearest(x, num=50):
    return ((x + num // 2) // num) * num
