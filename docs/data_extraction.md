# Data Extraction

## Data Extracted from Wikidata

Data are extracted for:

- Individuals
- Work of individuals
- Meta-data such as the Countries given a specifi geolocalisation

The scripts regarding the Wikidata Extraction can be found [here](../scraping/individuals/wikidata/)

The processus of extraction has been carried as followed:

1) Extraction of sub-occupation belonging to writer, scientist or artists as of June 2023 (the ontology evolves regularly).
2) Extraction of individuals and their meta-data (birth place, name, Catalog Identifiers, see description in the database creation) belonging to at least one of those occupations.
3) Extraction of meta-data of indiviudals'information (such as the country of the birth place or a nationality)
4) Extraction of sitelinks information (link to wikipedia pages).

Data have been extracted using [SPARQLWrapper](https://sparqlwrapper.readthedocs.io/en/latest/ ) given that Wikidata can be queries as a SQPARQL database.

## Data Extracted from Wikipedia

The scripts regarding the Wikidata Extraction can be found [here](../scraping/individuals/wikipedia/)

Initially information about individuals have been extracted from Wikipedia, using the Wikipedia API though python.

## Data Enriched for Population & GDP per capita

The GDP per capita & Population are added thought the following notebook [raw_to_db/insert_gdp_population_to_db.ipynb](../raw_to_db/insert_gdp_population_to_db.ipynb).

Population data is interpolatated for every decade.

To get information on how regions are associated to countries, check the [Google Sheet](<https://docs.google.com/spreadsheets/d/1MGNzF-CcGMDkyYR0M1CS2lzJrGc4bGDVR9zj7H68uA8/edit#gid=1495995572>)
