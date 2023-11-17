# Unseen Species Model

This model is developped by Mike Kestemont & Folgert Karsdorp

Run:

```bash
cd unseen_species_model
python run run_trends_works.py
``````

This command creates the .csv file [unseen_species_model/df_indi_works.csv](../unseen_species_model/df_indi_works.csv). For the model, when an individual has not work mentionned anywhere, we kept the individual and assigned the value 0.

Then run [unseen_species_model/regression.ipynb](../unseen_species_model/regression.ipynb)
The notebook output the following [file](../unseen_species_model/estimations-per-region-3072023.csv)
