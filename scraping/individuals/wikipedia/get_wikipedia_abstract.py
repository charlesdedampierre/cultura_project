import requests


def get_wiki_abstract(title="Tadao_Ando", wiki="en"):
    """Get the wikipedia abstract of a page

    Parameters
    ----------
    title : str
       Title of the page (the title has to fit the wikipedia language), by default "Tadao_Ando"
    wiki : str
        Nationality of the wikipedia, by default "en"

    Returns
    -------
    str
        Outputs the abstract
    """

    query_wiki_abstract = f"https://{wiki}.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro&explaintext&redirects=1&titles={title}"

    res = requests.get(query_wiki_abstract).json()
    page_id = list(res["query"]["pages"].keys())[0]
    wiki_abstract = res["query"]["pages"][page_id]["extract"]

    return wiki_abstract
