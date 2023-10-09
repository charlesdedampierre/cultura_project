from wikidata_extract import WikidataApi

query = """

Select ?item ?itemLabel
WHERE {
  
  ?item wdt:P279* wd:Q901

    # wd:Q901 scientifi
   
  SERVICE wikibase:label { bd:serviceParam wikibase:language 'en'. }
  
  }"""


res = WikidataApi(query)
res.columns = ["item", "item_name"]
res.to_csv("data/science_sub_occupations.csv")

print(res)
