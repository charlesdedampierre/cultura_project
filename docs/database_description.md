# Cultura 1.0 Database

## Overview

Cultura 1.0 is a database that contains information on Artists & Scientists born before 1850 from different authority files such as GND, VIAF, The Library of Congress etc.

The Database is designed to provide a comprehensive collection of structured information about various cultural entities such as artists, scientists and their works, as well as enriched data about their country of origins.

The data is organized in a SQLite3 format, making it easy to query and retrieve relevant information.

## Features

- Authority files data extracted fromthe Wikidata Portal
- Comprehensive information about cultural & scientific entities
- SQLite3 format for easy querying and integration
- Manually Enriched

## Database Structure

The Cultura 1.0 database follows a relational structure, with tables representing different entities and their attributes. Here is an overview of the main tables:

The merging of the id is carried out thanks to the Wikidata_id of entities.

- `individual_gender`: store information about the gender of individuals.
- `individual_nationality`: store information about the gender of individuals.
- `individual_birthcity`: store information about the birthcity of individuals.
- `birthcity`: store information about meta-data of  birthcities (location, country etc).
- `individual_identifiers`: store information about Authority Files Identifiers of individuals.
- `individual_wikipedia`: store information Wikipedia Page in 280 language of individuals.
- `individual_occupations`: store information about the occupations of individuals.
- `individuals_main_information`: store information about main information about individuals (birthyear, cleaned country of origin).
- `individuals_regions`: store information about the regions an individual belongs to.
- `individual_viaf_id`: store information about the VIAF Id of individuals.
- `country_continent`: store information about country and continents and their wikidata ids.
- `individual_created_work`: store information the different works of individuals.
- `identifiers`: store information the meta-data of Authority Files.
- `created_work_identifiers`: store information about Authority Files Identifiers of works.
- `created_work`: store information about the meta-data of individuals' works.
- `notable_work`: store information about the meta-data of individuals' notable works.

## Installation

Install SQLite3 on your system if it's not already installed.

```shell
pip install sqlite3
```

## Examples

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('cultura_1.db')

# Chose a table to extract
table_name = 'individuals_main_information'

# Load the table as a pandas DataFrame
df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
```