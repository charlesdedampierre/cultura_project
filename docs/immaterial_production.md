## Immaterial Production

The scores of indiviudals and regions are created with [make_individuals_and_regions_score.ipynb](../immaterial_index/make_individuals_and_regions_score.ipynb).

- Regions: the Score of a region is the number of individuals dead in that region and referenced in an online catalog.
- Individuals: The Score of an indiviudal is the number of references in online catalogs. For instance Leo Tolstoy as a score of 52 because he exists in the Online Catalogs of 52 different countries.

To visualize the  figures, call the following R functio .in [plot_trend R script](../immaterial_index/figures_trends_R)

<img src="../images/test.png" width="70%" height="70%" align="center" />

- The blue line is the loess regression on the number of works per decade. The scale has been normalized between 0 and 1 where 1 is the higest point on the graph.

- The red dots at individuals. Their score is based on the number of online catalogs they appear on.

Both scores have been normalizd bewteen 0 and 1 where 1 is the highest value on the current graph for both score.
