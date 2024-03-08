import pandas as pd

df = pd.read_csv("data/df_indi_works.csv", index_col=0)
# df = pd.read_csv("data/df_indi_works_clean_gdp.csv", index_col=0)

print(len(df))

regions = pd.read_csv(
    "data/ENS - Cultural Index - Countries Databases - region_level.csv"
)
regions = regions[regions["level"] == 2]
regions = set(regions["region_name"])
df = df[df["region_name"].isin(regions)]
df["century"] = df["decade"].round(-2)
df.head(n=10)
max(df.decade)


import matplotlib.pyplot as plt
import numpy as np

num_knots = 10
knots = np.linspace(df["century"].min(), df["century"].max(), num_knots)

fig, ax = plt.subplots()
(df.groupby(["decade", "individual_wikidata_id"])["count_works"].sum() + 1).droplevel(
    level="individual_wikidata_id"
).plot(style=".", alpha=0.1, logy=True, ax=ax)

for knot in knots:
    ax.axvline(knot, color="0.1", alpha=0.1, ls="--")


df["count"] = df["count_works"]
df_m = df.copy()
df_m = df_m[df_m["count"].isin({0, 1, 2})]  # Not more ?
df_m["y"] = df_m["count"].map({0: 0, 1: 0, 2: 1})
df_m.sample(10)

print(len(df_m))

import bambi as bmb
import arviz as az

iknots = knots[1:-1]

print(iknots)
"""
sample = df_m

df_m[['decade', 'y']].sample(10)

priors = {
    "Intercept": bmb.Prior("Normal", mu=0, sigma=2.5),
    "bs(decade, knots = iknots, intercept = True)|region_name": bmb.Prior(
        "Normal", mu=0, sigma=bmb.Prior("HalfNormal", sigma=2.5))
}

m_splines_vs = bmb.Model(
    'y ~ 1 + (bs(decade, knots=iknots, intercept=True)|region_name)', 
    sample, family='bernoulli', priors=priors)
m_splines_vs"""

#  Global Spline Analysis with Varying Intercepts for Region

sample = df_m

priors = {
    "Intercept": bmb.Prior("Normal", mu=0, sigma=5),
    "common": bmb.Prior("Normal", mu=0, sigma=5),
    "1|region_name": bmb.Prior("Normal", mu=0, sigma=bmb.Prior("HalfNormal", sigma=5)),
}

m_splines_vi = bmb.Model(
    "y ~ bs(decade, knots=iknots, intercept=True) + (1|region_name)",
    sample,
    family="bernoulli",
    priors=priors,
)


# Main script
p_splines_vs = m_splines_vi.fit(
    draws=1000, chains=4, inference_method="nuts_numpyro"
)  # important to run faster and sample more efficiently

az.summary(p_splines_vs)


def plot_knots(knots, ax):
    for knot in knots:
        ax.axvline(knot, color="0.1", alpha=0.4)
    return ax


def plot_predictions(
    data, idata, model, region=None, ax=None, plot_knot_lines=True, color="C0"
):
    if ax is None:
        fig, ax = plt.subplots()

    new_data = {}
    if region is not None:
        data = data[data["region_name"] == region]
        new_data["region_name"] = [region] * 500
    new_data["decade"] = np.linspace(
        data["decade"].min(), data["decade"].max(), num=500
    )
    new_data = pd.DataFrame(new_data)

    model.predict(idata, data=new_data)

    posterior_stacked = az.extract(idata)
    # Extract these predictions
    y_hat = posterior_stacked["y_mean"]

    # Compute the mean of the predictions, plotted as a single line.
    y_hat_mean = y_hat.mean("sample")

    # Compute 94% credible intervals for the predictions, plotted as bands
    hdi_data = np.quantile(y_hat, [0.11, 0.89], axis=1)

    # Plot predicted line
    ax.plot(new_data["decade"], y_hat_mean, color=color, label=region)

    # Plot credibility bands
    ax.fill_between(
        new_data["decade"], hdi_data[0], hdi_data[1], alpha=0.4, color=color
    )

    # Add knots
    if plot_knot_lines:
        plot_knots(knots, ax)
    ax.set(xlabel="time", ylabel="p(n_obs=2)")


region = "Chinese world"
fig, ax = plt.subplots(figsize=(6, 4))
plot_predictions(sample, p_splines_vs, m_splines_vi, region, ax=ax)

# fig.savefig('results/china_spline.png', dpi=300)


fig, axes = plt.subplots(ncols=4, nrows=5, figsize=(10, 8), constrained_layout=True)
axes = axes.flatten()

for i, region in enumerate(sorted(df_m["region_name"].unique())):
    plot_predictions(
        sample,
        p_splines_vs,
        m_splines_vi,
        region,
        ax=axes[i],
        color="k",
        plot_knot_lines=False,
    )
    axes[i].set(title=region, xlabel="", ylabel="")

fig.supylabel("p(n_obs=2)")
fig.supxlabel("time")


def plot_estimations(
    data,
    obs_data,
    idata,
    model,
    region=None,
    ax=None,
    logy=False,
    plot_knot_lines=True,
    color="C0",
):
    if ax is None:
        fig, ax = plt.subplots()

    new_data = {}
    data = data[data["region_name"] == region]
    obs_data = obs_data[obs_data["region_name"] == region]

    new_data["decade"] = data["decade"].values
    new_data["region_name"] = [region] * len(data["decade"].values)

    new_data = pd.DataFrame(new_data)

    model.predict(idata, data=new_data)

    posterior_stacked = az.extract(idata)
    # Extract these predictions
    p = posterior_stacked["y_mean"].values
    l = (2 * p) / (1 - p)
    f0 = 1 / (l + (l**2) / 2)

    decades = np.array(sorted(data["decade"].unique()))

    N_est = np.zeros((len(decades), f0.shape[1]))
    unseen = np.zeros((len(decades), f0.shape[1]))

    for i, decade in enumerate(decades):
        n_obs_di = data.loc[
            data["decade"] == decade, "individual_wikidata_id"
        ].nunique()
        mask = (new_data["decade"] == decade).astype(int).values[:, None]
        f0_di = (f0 * mask).sum(0)
        S_di = n_obs_di + f0_di
        N_est[i] = S_di
        unseen[i] = f0_di

    # Compute 94% credible intervals for the predictions, plotted as bands
    hdi_data = np.quantile(N_est, [0.11, 0.89], axis=1)

    # Plot predicted line
    ax.plot(decades, N_est.mean(1), color=color, label=region)

    df[df["region_name"] == region].groupby("decade")[
        "individual_wikidata_id"
    ].count().plot(ax=ax, ls="--", color="red")

    # Plot credibility bands
    ax.fill_between(decades, hdi_data[0], hdi_data[1], alpha=0.4, color=color)

    # Add knots
    if plot_knot_lines:
        plot_knots(knots, ax)
    ax.set(xlabel="time", ylabel="Estimated diversity")
    if logy:
        ax.set_yscale("log")

    return unseen, N_est, hdi_data, decades


plot_estimations(
    sample,
    df,
    p_splines_vs,
    m_splines_vi,
    "Low countries",
    color="k",
    plot_knot_lines=False,
    logy=False,
)


fig, axes = plt.subplots(ncols=4, nrows=5, figsize=(10, 8), constrained_layout=True)
axes = axes.flatten()

results = {}
for i, region in enumerate(sorted(df_m["region_name"].unique())):
    f0, N_est, hdi, decades = plot_estimations(
        sample,
        df,
        p_splines_vs,
        m_splines_vi,
        region,
        ax=axes[i],
        color="k",
        plot_knot_lines=False,
    )
    axes[i].set(title=region, xlabel="", ylabel="")
    results[region] = f0, N_est, hdi, decades

fig.supylabel("Estimated diversity")
fig.supxlabel("time")


# fig.savefig('results/estimated_diversity_per_region.png', dpi=300)


def plot_trend(
    decades, N_est, hdi_data, color="C0", label=None, ax=None, logy=False, figsize=None
):
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)

    # Plot predicted line
    ax.plot(decades, N_est.mean(1), color=color, label=label)

    # Plot credibility bands
    ax.fill_between(decades, hdi_data[0], hdi_data[1], alpha=0.4, color=color)

    ax.set(xlabel="time", ylabel="Estimated diversity")
    if logy:
        ax.set_yscale("log")

    return ax


region = "Japan"

f0, N_est, hdi, decades = results[region]

ax = plot_trend(decades, N_est, hdi, label=region)
ax.set_xlim(-500, 1900)


regions = "United Kingdom", "France", "Chinese world", "Japan"

fig, ax = plt.subplots()
for i, region in enumerate(regions):
    f0, N_est, hdi, decades = results[region]
    ax = plot_trend(decades, N_est, hdi, color=f"C{i}", logy=False, label=region, ax=ax)
ax.set_xlim(1000, 1850)
ax.legend()


table = []
for region in results:
    _, N_est, hdi, decades = results[region]
    N_est = N_est.mean(1)
    li, ui = hdi[0], hdi[1]
    print(N_est.shape, li.shape, ui.shape, decades.shape)
    table.append(
        pd.DataFrame(
            {
                "N_est": N_est,
                "lower": li,
                "upper": ui,
                "decade": decades,
                "region": [region] * N_est.shape[0],
            }
        )
    )
table = pd.concat(table)
table.head()


table.to_csv("results/estimations_charles_tmux.csv", index=False)
# table.to_csv("results/estimations.csv", index=False)
# table.to_csv("results/estimations_clean_gdp.csv", index=False)
