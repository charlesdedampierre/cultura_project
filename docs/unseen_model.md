# Unseen Species Model

This model is developped by Mike Kestemont & Folgert Karsdorp

Firts, run a script to get the a dataset of the number of works for every individual. This dataset will be used by the unseen species model.

```bash
cd unseen_species_model
python run run_trends_works.py
``````

This command creates the .csv files [df_indi_works.csv](../unseen_species_model/data/df_indi_works.csv) and [df_indi_works_clean_gdp.csv](../unseen_species_model/data/df_indi_works_clean_gdp.csv). For the model, when an individual has not work mentionned anywhere, we kept the individual and assigned the value 0.

Then run [unseen_species_model/regression.ipynb](../unseen_species_model/regression.ipynb)
The notebook output the following [file](../unseen_species_model/results/estimations.csv)
