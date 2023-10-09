from wikidata_extract import WikidataApi

query = """

Select ?item ?itemLabel
WHERE {
  
  ?item wdt:P279* wd:Q36180

    # wd:Q36180 writer
   
  SERVICE wikibase:label { bd:serviceParam wikibase:language 'en'. }
  
  }"""


res = WikidataApi(query)
# res.columns = ["item", "item_name"]
res.to_csv("data/writer_sub_occupations.csv")

print(res)
