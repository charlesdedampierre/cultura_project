## Bayesian Statistics

1) The [make_region_score.ipynb](../Immaterial_index/make_region_score.ipynb) creates the following columns in the Sqlite3 db:

- region_score
- region_score_top_10 (region score based on the top 50% notable people)
- region_score_top_10 (region score based on the top 10% notable people)

2) Run the following script [bayesian_statistics/make_stats.ipynb](../bayesian_statistics/make_stats.ipynb) creates the following files (depending on the region_score_{} input from the sqlite3)

- data_stats_filtered.csv (table with the stats of regions merged with region score for all individuals)
- data_stats_filtered_top_50.csv (table with the stats of regions merged with region score based on the top 50% notable people)
- data_stats_filtered_top_10.csv (table with the stats of regions merged with region score based on the top 10% notable people)

3) Run [bayesian_statistics/BRM.ipynb](../bayesian_statistics/BRM.ipynb) to launch the analysis

the BRM_normal_top_50_top_10_top_analysis.ipynb is the script for Bayesian regression analysis with the models taking into account the scores for
the top 50% notable people and the top 10% notable people.
