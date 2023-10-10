## Immaterial Production

- Regions' Immaterial scores are made with [immaterial_index/make_region_score.ipynb](../immaterial_index/make_region_score.ipynb).The Score of a region is the number of individuals born in that region and referenced in an online catalog.

- Individuals' Immaterial scores are made with [immaterial_index/make_individuals_score.ipynb](../immaterial_index/make_individuals_score.ipynb).The Score of an indiviudal is the number of references in online catalogs. For instance Leo Tolstoy as a score of 52 because he exists in the Online Catalogs of 52 different countries.

To visualize the  figures, call the following R function. You can Change the parameters at the beginning of the [plot_trend R script](../immaterial_index/figures_trends_R/index.R). To visualize two trends at the same time, use [figures_trends_R/index.R](../immaterial_index/figures_trends_R/index_comparison.R)

```bash
Rscript Immaterial_index/figures_trends_R/index.R
```

<img src="../images/test.png" width="70%" height="70%" align="center" />

- The blue line is the loess regression on the number of works per decade. The scale has been normalized between 0 and 1 where 1 is the higest point on the graph.

- The red dots at individuals. Their score is based on the number of online catalogs they appear on.

Both scores have been normalizd bewteen 0 and 1 where 1 is the highest value on the current graph for both score.
