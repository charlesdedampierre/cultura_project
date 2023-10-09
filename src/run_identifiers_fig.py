import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from functions_env import DATA_PATH


def make_figure(
    df_graph_bis,
    region_name,
    min_decade=1200,
    max_decade=1800,
    top_identifiers=5,
    width=1200,
    height=600,
):
    df_fig = df_graph_bis[df_graph_bis["region_name"] == region_name]
    df_fig = df_fig[df_fig["decade"] <= max_decade]
    df_fig = df_fig[df_fig["decade"] >= min_decade]

    one_id_country = (
        df_fig.groupby(["country_name", "identifier_name"])["score"].sum().reset_index()
    )
    one_id_country = one_id_country.sort_values(
        ["country_name", "score"], ascending=(False, False)
    )
    one_id_country = one_id_country.groupby("country_name").head(1)
    one_id_country = list(one_id_country["identifier_name"])

    df_fig = df_fig[df_fig["identifier_name"].isin(one_id_country)]
    top_ids = (
        df_fig.groupby(["identifier_name"])["score"]
        .sum()
        .reset_index()
        .sort_values("score", ascending=False)
    )

    # top_ids = top_ids[top_ids['identifier_name']!='all_identifiers']
    top_ids = list(top_ids["identifier_name"][:top_identifiers])
    df_fig = df_fig[df_fig["identifier_name"].isin(top_ids)]
    df_fig_mean = df_fig.groupby(["decade"])["score"].mean().reset_index()
    df_fig_mean["identifier_name"] = "average"

    # df_fig = pd.concat([df_fig, df_fig_mean])

    fig = px.line(
        df_fig,
        x="decade",
        y="score",
        color="identifier_name",
        width=width,
        height=height,
        title=region_name,
        template="simple_white",
        category_orders={"identifier_name": top_ids},
    )
    # line_shape='spline')

    # fig.update_layout(legend=dict(title=dict(text='Top 5 Immaterial Production')))
    fig.update_traces(opacity=0.25)

    fig2 = px.line(
        df_fig_mean,
        x="decade",
        y="score",
        color="identifier_name",
        width=width,
        height=height,
        title=region_name,
        template="simple_white",
    )
    # line_shape='spline')

    fig2.update_traces(line=dict(width=3))
    fig3 = go.Figure(data=fig.data + fig2.data)
    fig3.update_layout(
        xaxis_title="",
        yaxis_title="Number of Individuals",
        template="simple_white",
        width=width,
        height=height,
        title=region_name,
    )

    # Update the layout with the category order

    # ig3.for_each_trace(lambda t: t.update(name=legend_order.index(t.name)))
    fig3.update_layout(legend=dict(title=dict(text="Identifiers")))
    # fig3.update_layout(category_orders={'Identifiers': top_ids})
    fig3.update_layout(xaxis=dict(dtick=100))

    return fig3


if __name__ == "__main__":
    df_fig = pd.read_csv(DATA_PATH + "/df_identifiers_trends.csv")
    df_fig["score"] = np.log(df_fig["score"] + 1)

    region_name = "Chinese world"
    min_decade = -500
    max_decade = 1800

    fig3 = make_figure(
        df_fig,
        region_name=region_name,
        min_decade=min_decade,
        max_decade=max_decade,
        top_identifiers=15,
        width=1200,
        height=600,
    )

    fig3.show()
    # fig3.write_image(f"graph_18_05/{region_name}_identifiers.png", scale=7)
