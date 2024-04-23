import pandas as pd
import bambi as bmb
import arviz as az
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("data/df_indi_works_gender.csv", index_col=0)

regions = pd.read_csv(
    "data/ENS - Cultural Index - Countries Databases - region_level.csv"
)
regions["region_name"][regions["region_name"] == "Slav world"] = "East Slavic"

regions = regions[regions["level"] == 2]
regions = set(regions["region_name"])
df = df[df["region_name"].isin(regions)]

df = df[
    ~((df["region_name"] == "Italy") & (df["decade"] < 500))
] 

df["century"] = df["decade"].round(-2)
df = df[df["gender"].isin(["male", "female"])]

df["count"] = df["count_works"]
df_m = df.copy()
df_m = df_m[df_m["count"].isin({0, 1, 2})]  # Not more ?
df_m["y"] = df_m["count"].map({0: 0, 1: 0, 2: 1})

# about 6% of women compared to men
df_m = df_m[df_m["decade"] < 1880]

# knots
num_knots = 10
knots = np.linspace(df["century"].min(), df["century"].max(), num_knots)
iknots = knots[1:-1]

sample = df_m.copy()
# sample = sample.sample(5000, random_state=42)

models = {}

priors = {
    "Intercept": bmb.Prior("Normal", mu=0, sigma=5),
    "common": bmb.Prior("Normal", mu=0, sigma=5),
    "1|region_name": bmb.Prior("Normal", mu=0, sigma=bmb.Prior("HalfNormal", sigma=5)),
}

gender_model = bmb.Model(
    "y ~ bs(decade, knots=iknots, intercept=True) + gender + (1|region_name)",
    sample[["decade", "region_name", "gender", "y"]],
    family="bernoulli",
    priors=priors,
)

gender_model_fitted = gender_model.fit(
    draws=1000,
    chains=4,
    inference_method="nuts_numpyro",
    idata_kwargs={"log_likelihood": True},
)  # important to run faster and sample more efficiently

models["gender-model"] = gender_model_fitted
az.waic(models["gender-model"])

# SECOND MODEL
priors_base_model = {
    "Intercept": bmb.Prior("Normal", mu=0, sigma=5),
    "common": bmb.Prior("Normal", mu=0, sigma=5),
    "1|region_name": bmb.Prior("Normal", mu=0, sigma=bmb.Prior("HalfNormal", sigma=5)),
}

base_model = bmb.Model(
    "y ~ bs(decade, knots=iknots, intercept=True) + (1|region_name)",
    sample[["decade", "region_name", "y"]],
    family="bernoulli",
    priors=priors_base_model,
)

base_model_fitted = base_model.fit(
    draws=1000,
    chains=4,
    inference_method="nuts_numpyro",
    idata_kwargs={"log_likelihood": True},
)  # important to run faster and sample more efficiently


models["base-model"] = base_model_fitted
az.waic(models["base-model"])

waic_compare = az.compare(models, ic="LOO")
az.plot_compare(waic_compare, insample_dev=True)

waic_compare = az.compare(models, ic="LOO")
waic_compare.to_csv("results/gender/model_comparison.csv")

compare_plot = az.plot_compare(waic_compare, insample_dev=True)
fig = compare_plot.get_figure()
fig.set_size_inches(8, 4)  # Adjust size as needed
fig.tight_layout()

fig.savefig("results/gender/compare_plot.png")


list_summaries = []

for key, item in models.items():
    res = az.summary(item)
    res["model"] = key
    list_summaries.append(res)


from datetime import datetime

df_summaries = pd.concat([x for x in list_summaries])
# Add a column with the current time
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
df_summaries["time"] = current_time
df_summaries.to_csv("results/gender/model_results.csv")
