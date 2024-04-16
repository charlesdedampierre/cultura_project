import pandas as pd
import bambi as bmb
import arviz as az
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

import numpyro
import jax
print(jax.local_device_count())

numpyro.set_host_device_count(4)

df = pd.read_csv("data/df_indi_works_occupations.csv", index_col=0)
print(df.occupation.value_counts())

regions = pd.read_csv(
    "data/ENS - Cultural Index - Countries Databases - region_level.csv"
)
regions["region_name"][regions["region_name"] == "Slav world"] = "East Slavic"
regions = regions[regions["level"] == 2]
regions = regions[regions["region_name"] != "Balkans"]
regions = regions[
    regions["region_name"] != "Eastern Europe"
]  # remove because it takes East Slavic and Central Europe
regions = set(regions["region_name"])
df = df[df["region_name"].isin(regions)]

df["century"] = df["decade"].round(-2)

df = df[~((df["region_name"] == "Italy") & (df["decade"] < 500))]
df = df[~((df["region_name"] == "Portugal") & (df["decade"] < 500))]
df = df[~((df["region_name"] == "Spain") & (df["decade"] < 500))]
df = df[~((df["region_name"] == "Arabic world") & (df["decade"] < 500))]
df = df[~((df["region_name"] == "France") & (df["decade"] < 500))]
df = df[~((df["region_name"] == "United Kingdom") & (df["decade"] < 500))]
df = df[~((df["region_name"] == "Low countries") & (df["decade"] < 500))]
df = df[~((df["region_name"] == "East Slavic") & (df["decade"] < 500))]
df = df[~((df["region_name"] == "Central Europe") & (df["decade"] < 500))]
df = df[~((df["region_name"] == "German world") & (df["decade"] < 500))]
df = df[~((df["region_name"] == "Latin world") & (df["decade"] > 500))]


# Avoid overlapping with Antiquity

df["count"] = df["count_works"]
df_m = df.copy()
df_m = df_m[df_m["count"].isin({0, 1, 2})]  # Not more ?
df_m["y"] = df_m["count"].map({0: 0, 1: 0, 2: 1})

# knots
num_knots = 10
knots = np.linspace(df["century"].min(), df["century"].max(), num_knots)
iknots = knots[1:-1]

sample = df_m.copy()
#sample = sample.sample(4000, random_state=42)

# DIFFERENT EQUATIONS

models = {}


# MODEL 1
equation = "y ~ 1"

base_model = bmb.Model(
    equation,  # variance spline and variance intercept model
    sample,
    family="bernoulli",
    priors={
        "Intercept": bmb.Prior("Normal", mu=0, sigma=2.5),
    },
)

base_model_fitted = base_model.fit(
    draws=1000,
    chains=4,
    inference_method="nuts_numpyro",
    idata_kwargs={"log_likelihood": True},
)

models[equation] = base_model_fitted
az.waic(models[equation])


# MODEL 2
equation = "y ~ bs(decade, knots=iknots, intercept=True)"
priors = {
    "Intercept": bmb.Prior("Normal", mu=0, sigma=5),
    "common": bmb.Prior("Normal", mu=0, sigma=5),
}

base_model = bmb.Model(
    equation, sample[["decade", "y"]], family="bernoulli", priors=priors
)


base_model_fitted = base_model.fit(
    draws=1000,
    chains=4,
    inference_method="nuts_numpyro",
    idata_kwargs={"log_likelihood": True},
)  # important to run faster and sample more efficiently

models[equation] = base_model_fitted


# MODEL 3
equation = "y ~ bs(decade, knots=iknots, intercept=True) + (1|region_name)"
priors = {
    "Intercept": bmb.Prior("Normal", mu=0, sigma=5),
    "common": bmb.Prior("Normal", mu=0, sigma=5),
    "1|region_name": bmb.Prior("Normal", mu=0, sigma=bmb.Prior("HalfNormal", sigma=5)),
}

base_model = bmb.Model(
    equation, sample[["decade", "region_name", "y"]], family="bernoulli", priors=priors
)


base_model_fitted = base_model.fit(
    draws=1000,
    chains=4,
    inference_method="nuts_numpyro",
    idata_kwargs={"log_likelihood": True},
)  # important to run faster and sample more efficiently

models[equation] = base_model_fitted

# MODEL 4
equation = "y ~ bs(decade, knots=iknots, intercept=True) + occupation +(1|region_name)"


priors = {
    "Intercept": bmb.Prior("Normal", mu=0, sigma=5),
    "common": bmb.Prior("Normal", mu=0, sigma=5),
    "1|region_name": bmb.Prior("Normal", mu=0, sigma=bmb.Prior("HalfNormal", sigma=5)),
}

base_model = bmb.Model(equation, sample, family="bernoulli", priors=priors)

base_model_fitted = base_model.fit(
    draws=1000,
    chains=4,
    inference_method="nuts_numpyro",
    idata_kwargs={"log_likelihood": True},
)  # important to run faster and sample more efficiently

models[equation] = base_model_fitted

az.waic(models[equation])


# equation = "y ~ 1 + (bs(decade, knots=iknots, intercept=True)|region_name)"
# variance_model = bmb.Model(
#    equation,  # variance spline and variance intercept model
#     sample,
#     family="bernoulli",
#     priors={
#         "Intercept": bmb.Prior("Normal", mu=0, sigma=2.5),
#         "bs(decade, knots = iknots, intercept = True)|region_name": bmb.Prior(
#             "Normal",
#             mu=0,
#             sigma=bmb.Prior("HalfNormal", sigma=2.5),  # can't be negative
#         ),
#     },
# )

# variance_model_fitted = variance_model.fit(
#     draws=1000,
#     chains=4,
#     inference_method="nuts_numpyro",
#     idata_kwargs={"log_likelihood": True},
# )  # important to run faster and sample more efficiently

# models[equation] = (
#     variance_model_fitted
# )

# az.waic(models[equation])

# equation =   "y ~ (bs(decade, knots=iknots, intercept=True)|region_name) + occupation"
# equation = "y ~ 1 + (bs(decade, knots=iknots, intercept=True)|region_name)"


# #equation =  "y ~ (bs(decade, knots=iknots, intercept=True) + (1|region) + occupation"
# # OCCUPATION MODEL
# occupation_model = bmb.Model(
#    equation,
#     sample[["decade", "region_name", "occupation", "y"]],
#     family="bernoulli",
#     priors={
#         "Intercept": bmb.Prior("Normal", mu=0, sigma=5),
#         "common": bmb.Prior("Normal", mu=0, sigma=5),
#         "bs(decade, knots = iknots, intercept = True)|region_name": bmb.Prior(
#             "Normal",
#             mu=0,
#             sigma=bmb.Prior("HalfNormal", sigma=2.5),  # can't be negative
#         ),
#     },
# )
# equation =  "y ~ (bs(decade, knots=iknots, intercept=True) + (1|region)"
# equation =   "y ~ (bs(decade, knots=iknots, intercept=True)|region_name) + occupation"
# equation =  "y ~ (bs(decade, knots=iknots, intercept=True)|region_name)) + (1|occupation)"
# OCCUPATION MODEL
# occupation_model_variance = bmb.Model(
#     equation,
#     sample[["decade", "region_name", "occupation", "y"]],
#     family="bernoulli",
#     priors={
#         "Intercept": bmb.Prior("Normal", mu=0, sigma=5),
#         "common": bmb.Prior("Normal", mu=0, sigma=5),
#         "1|occupation": bmb.Prior(
#             "Normal", mu=0, sigma=bmb.Prior("HalfNormal", sigma=5)
#         ),
#         "bs(decade, knots = iknots, intercept = True)|region_name": bmb.Prior(
#             "Normal",
#             mu=0,
#             sigma=bmb.Prior("HalfNormal", sigma=2.5),  # can't be negative
#         ),
#     },
# )

# occupation_model_variance_fitted = occupation_model_variance.fit(
#     draws=1000,
#     chains=4,
#     inference_method="nuts_numpyro",
#     idata_kwargs={"log_likelihood": True},
# )  # important to run faster and sample more efficiently


# equation = 'y ~ bs(decade, knots=iknots, intercept=True) + occupation + (1|region_name)'
# priors = {
#     "Intercept": bmb.Prior("Normal", mu=0, sigma=5),
#     "common": bmb.Prior("Normal", mu=0, sigma=5),
#     "1|region_name": bmb.Prior("Normal", mu=0, sigma=bmb.Prior("HalfNormal", sigma=5))}

# category_model = bmb.Model(
#     'y ~ bs(decade, knots=iknots, intercept=True) + category + (1|region_name)',
#     sample[['decade','region_name', 'category', 'y']],
#     family='bernoulli',
#     priors=priors)

# category_model_fitted = category_model.fit(
#     draws=1000, chains=4, inference_method='nuts_numpyro',idata_kwargs={"log_likelihood": True}

# )

# models[
#    equation
# ] = category_model_fitted
# az.waic(
#     models[
#        equation
#     ]
# )

# # GET THE ALPHA FOR EVERY OCCUPATION

# forest_plot = az.plot_forest(
#     data=occupation_model_variance_fitted,
#     figsize=(6, 4),
#     var_names=["1|occupation"],
#     r_hat=True,
#     combined=True,
#     textsize=8,
#     ess=True,
# )

# fig = forest_plot[0].get_figure()
# fig.set_size_inches(8, 4)  # Adjust size as needed
# fig.tight_layout()

# fig.savefig("results/occupation/forest_plot_variance.png")

print("Save model comparison")

# Comparison Dataset
waic_compare = az.compare(models, ic="waic")
# Comparison Plot
compare_plot = az.plot_compare(waic_compare, insample_dev=True)
fig = compare_plot.get_figure()
fig.set_size_inches(20, 4)  # Adjust size as needed
fig.tight_layout()

fig.savefig("results/occupation/compare_plot_waic.png")

# Comparison Dataset

# waic_compare.to_csv("results/occupation/model_comparison.csv")

# Comparison Plot
waic_compare = az.compare(models, ic="LOO")
compare_plot = az.plot_compare(waic_compare, insample_dev=True)
fig = compare_plot.get_figure()
fig.set_size_inches(20, 4)  # Adjust size as needed
fig.tight_layout()
fig.savefig("results/occupation/compare_plot.png")


forest_plot = az.plot_forest(
    data=base_model_fitted,
    figsize=(6, 4),
    var_names=["occupation"],
    r_hat=True,
    combined=True,
    textsize=8,
    ess=True,
)

fig = forest_plot[0].get_figure()
fig.set_size_inches(8, 4)  # Adjust size as needed
fig.tight_layout()
fig.savefig("results/occupation/forest_plot.png")


# Save models CSV
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
df_summaries.to_csv("results/occupation/model_results.csv")

## Add the final results


def get_unseen_numbers_occupation(df, model, model_fitted, region="Chinese world"):

    new_data = {}

    data = df[df["region_name"] == region]
    new_data["decade"] = data["decade"].values
    new_data["occupation"] = data["occupation"].values
    new_data["region_name"] = [region] * len(data["decade"].values)

    new_data = pd.DataFrame(new_data)
    model.predict(model_fitted, data=new_data)
    posterior_stacked = az.extract(occupation_model_fitted)

    p = posterior_stacked["y_mean"].values
    l = (2 * p) / (1 - p)
    f0 = 1 / (l + (l**2) / 2)

    new_data["f0"] = pd.DataFrame(f0).apply(list, axis=1)
    new_data = new_data.sort_values(["decade", "occupation"])

    def sum_lists(group):
        return [sum(values) for values in zip(*group)]

    res = (
        new_data.groupby(["decade", "occupation"])["f0"]
        .apply(sum_lists)
        .rename("f0_list")
        .reset_index()
    )
    df_count = (
        data.groupby(["decade", "occupation"])["individual_wikidata_id"]
        .count()
        .rename("count_cps")
        .reset_index()
    )
    res = pd.merge(res, df_count, on=["decade", "occupation"])

    def add_count_cps(row):
        return [x + row["count_cps"] for x in row["f0_list"]]

    # Apply the function to each row
    res["N_est_list"] = res.apply(add_count_cps, axis=1)
    res["N_est"] = res["N_est_list"].apply(lambda x: np.mean(x))

    def compute_quantiles(row):
        return np.quantile(row, [0.11, 0.89])

    # Apply the function to each row in the N_est_list column
    res["quantiles"] = res["N_est_list"].apply(compute_quantiles)
    res["lower"] = res["quantiles"].apply(lambda x: x[0])
    res["upper"] = res["quantiles"].apply(lambda x: x[1])

    res = res.drop(["f0_list", "N_est_list", "quantiles"], axis=1)
    res["region_name"] = region

    return res


def get_unseen_numbers(df, model, model_fitted, region="Chinese world"):

    new_data = {}
    data = df[df["region_name"] == region]
    new_data["decade"] = data["decade"].values
    new_data["region_name"] = [region] * len(data["decade"].values)
    new_data = pd.DataFrame(new_data)
    model.predict(model_fitted, data=new_data)
    posterior_stacked = az.extract(model_fitted)

    p = posterior_stacked["y_mean"].values
    l = (2 * p) / (1 - p)
    f0 = 1 / (l + (l**2) / 2)

    decades = np.array(sorted(data["decade"].unique()))
    N_est = np.zeros((len(decades), f0.shape[1]))

    for i, decade in enumerate(decades):
        n_obs_di = data.loc[
            data["decade"] == decade, "individual_wikidata_id"
        ].nunique()
        mask = (new_data["decade"] == decade).astype(int).values[:, None]
        f0_di = (f0 * mask).sum(0)
        S_di = n_obs_di + f0_di
        N_est[i] = S_di

    # Compute 94% credible intervals for the predictions, plotted as bands
    hdi_data = np.quantile(N_est, [0.11, 0.89], axis=1)

    table = []
    table.append(
        pd.DataFrame(
            {
                "N_est": N_est.mean(1),
                "lower": hdi_data[0],
                "upper": hdi_data[1],
                "decade": decades,
                "region_name": [region] * N_est.shape[0],
            }
        )
    )
    table = pd.concat(table)
    return table


sample_base = sample.drop("occupation", axis=1)


# # GET THE RESULTS FOR THE CLASSICAL UNSEEN MODEL
# final_table = []
# for region in tqdm(sample_base.region_name.unique()):
#     table = get_unseen_numbers(
#         sample_base, base_model, base_model_fitted, region=region
#     )
#     final_table.append(table)

# df_final_table = pd.concat([x for x in final_table])
# df_final_table["model_type"] = "base_model"
# df_count = (
#     sample_base.groupby(["region_name", "decade"])["individual_wikidata_id"]
#     .count()
#     .rename("count_cps")
#     .reset_index()
# )
# df_final_table = pd.merge(df_final_table, df_count, on=["region_name", "decade"])
# df_final_table.to_csv("results/occupation/unseen_data.csv")


# GET THE RESULTS FOR THE CLASSICAL UNSEEN MODEL FOR OCCUPATION

# final_table = []
# for region in sample.region_name.unique():
#     table = get_unseen_numbers_occupation(
#         sample, occupation_model, occupation_model_fitted, region=region
#     )
#     final_table.append(table)

# df_final_table = pd.concat([x for x in final_table])
# df_final_table["model_type"] = "occupation_model"
# df_final_table.to_csv("results/occupation/unseen_data_occupation.csv")
