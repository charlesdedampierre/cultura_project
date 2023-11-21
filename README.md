<img src="images/Cultura 1.0 - cultura_logo.png" width="50%">

[![PyPI - Python](https://img.shields.io/badge/python-v3.11-blue.svg)](https://pypi.org/project/bunkatopics/)

This project incorporates two paper:

- A [CHR](https://2023.computational-humanities-research.org/) paper (Using Online Catalogs to Estimate Economic Development in Classical Antiquity, by Charles de Dampierre, Valentin Thouzeau, Nicolas Baumard) that is only associated with the Database Extraction and ETL Pipeline and the Computing Immaterial Production. Figures associated with the paper can be found in the following script
  - [Latin World Cultural Index](immaterial_index/figures_trends_R/index_italy.R)
  - [Greek World Cultural Index](immaterial_index/figures_trends_R/index_greece.R)
  - [Greek & Latin Worlds Cultural Index](immaterial_index/figures_trends_R/index_greece_italy.R)

- A broder paper that includes the Unseen Species Model and the Bayesian Statistics thought the contributions of Mike Kestemont & Folgert Karsdorp.

The Cultura Project is a research project aiming at re-construction the dynamics of past Civilisations using data from Catalogs Online (Library of Congress, GND, VIAF etc).

The Project has the following steps:

- [Database Extraction and ETL Pipeline](docs/database_description.md)
- [Computing Immaterial Production](docs/immaterial_production.md)
- [Applying Unseen Species Model to the Immaterial Production](docs/unseen_model.md)
- [Applying Bayesian Statistics for the relationship between GDP per capita and the Immaterial Index](docs/bayesian_statistics.md)

## Implementation

The Cultural 1.0 Database can be downloaded on the [OSF Forum](https://osf.io/2euxr/)

In the env file, add the path to the cultural_1.db (DB_PATH = 'PATH_TO_CULTURA_1.0_DB')

Then, change the file into an environement variable

```bash
pip install python-dotenv # install dot-env package
cp env .env
```

In order to be able to run the code, create a new environement using Poetry

```bash
poetry install # install the packages in the poetry.lock file
poetry shell # activate the environment
```

<img src="images/log.png" width="50%">
