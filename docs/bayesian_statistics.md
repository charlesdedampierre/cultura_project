### Bayesian Statistics

1) The [make_region_score.ipynb](../Immaterial_index/make_region_score.ipynb) creates the following column in the Sqlite3 db: region_score

2) Run the following script [bayesian_statistics/make_stats.ipynb](../bayesian_statistics/make_stats.ipynb) creates

- [data_stats.csv](../bayesian_statistics/results/data_stats.csv)
- [data_stats_clean_gdp.csv](../bayesian_statistics/results/data_stats_clean.csv)
- [data_stats_interpolated.csv](../bayesian_statistics/results/data_stats_interpolated.csv)
- [data_stats_interpolated_clean_gdp.csv](../bayesian_statistics/results/data_stats_interpolated_clean_gdp.csv)

This script merge information about GDP per capita, population, Immaterial Index and corrected Immaterial Index, using interpolation or not on 'clean' and 'not cleaned' GDP data.

3) Run [bayesian_statistics/BRM.ipynb](../bayesian_statistics/BRM.ipynb) to launch the analysis
