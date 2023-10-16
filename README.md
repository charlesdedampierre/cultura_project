<img src="images/Cultura 1.0 - cultura_logo.png" width="50%">

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

<img src="images/log.png" width="50%">
