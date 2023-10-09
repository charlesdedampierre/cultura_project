# Cultura Project

## Implementation

The Cultural 1.0 Database can be downloaded on the [OSF Forum](https://osf.io/2euxr/)

In the env file, add the path to the cultural_1.db (DB_PATH = 'PATH_TO_CULTURA_1.0_DB')

Then, change the file into an environement variable

```bash
pip install python-dotenv # install dot-env package
cp env .env
```

## Database Extraction and ETL Pipeline

For more information on the extraction  process of data, find information [here](docs/data_extraction.md)
For more information about the dababase, you can find information [here](docs/database_description.md).

## Creation of the Immaterial Production Trends

### Insertion of data for visualization

- The Region Score is made thought the following notebook [notebooks/make_region_score.ipynb](notebooks/make_region_score.ipynb).The Score of region is the number of individuals at each time period with at least one reference is a Online National Catalog.

- The Individuals Score is made thought the following notebook [notebooks/make_individuals_score.ipynb](notebooks/make_individuals_score.ipynb).The Score of an indiviudal is the number of references in online national catalogs. For instance Leo Tolstoy as a score of 52 because he exists in the Online Catalogs of 52 different countries.

- The GDP per capita & Population are addedthought the following notebook [notebooks/insert_gdp_to_db.ipynb](notebooks/insert_gdp_to_db.ipynb).

### Visualization

- Visualisation of the Number of individuals per decade with Rscript

Change the paramter at the beginning of the [plot_trend R script](r_visual_scripts/plot_trend.R) and display graph with the following command:

```bash
python src/run_trends.py
# output --> data/
Rscript r_visual_scripts/plot_trend.R # call the Rscript
# output --> test.png
```

### Description of the figures

- The blue line is the loess regression on the number of works per decade. The scale has been normalized between 0 and 1 where 1 is the higest point on the graph.

- The red dots at individuals. Their score is based on how much works who know they haev done. Everything has been normalizd bewteen 0 and 1 where 1 is the individual with the higest number of works on the graph.

<img src="images/test.png" width="50%" height="50%" align="center" />

### Run Identifiers Graph

```bash
python src/run_identifiers.py
# output --> data/df_identifiers_trends.csv
python src/run_identifier_fig_.py
# output --> image.png
```

## Implementation of the Unseen Species Model

For more information about the Unseen Species Model, you can find information [here](docs/unseen_model.md).

Check the directory [unseen_species_model](unseen_species_model/) for the code to the analysis

The input of [unseen_species_model/regression.ipynb](unseen_species_model/regression.ipynb) is [data/df_indi_works.csv](data/df_indi_works.csv) created in [src/run_trends_works.py](src/run_trends_works.py). When an individual has not work mentionned anywhere, we kept the individual and assigned the value 0.
Output is [unseen_species_model/estimations-per-region-3072023.csv]/

## Bayesian Statistics

the Input for the different notebooks related to Bayesian Statistics is a .csv: [stats_correlation/data_stats_filtered.csv](stats_correlation/data_stats_filtered.csv) and is made with the following notebook [stats_correlation/make_stats.ipynb](stats_correlation/make_stats.ipynb)

the Data for GDP and Population are added from notebooks/plot_gdp.ipynb .It uses files downloaded from the following sheet [Google Sheet](https://docs.google.com/spreadsheets/d/1MGNzF-CcGMDkyYR0M1CS2lzJrGc4bGDVR9zj7H68uA8/edit#gid=1495995572)

```bash
Rscript stats_correlation/script_estimate_GDP.R
```

### Running Stats

Check the directory [stats_correlation](stats_correlation/) for the code to the analysis

### Ploting the score for every region

--> notebooks/plot_facet_catalog_index.ipynb
