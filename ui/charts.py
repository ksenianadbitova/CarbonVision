import plotly.express as px
import pandas as pd


def biomass_chart(series, aoi_name):
    df = pd.DataFrame(series)
    fig = px.line(
        df, x="year", y="carbon_t_ha",
        title=f"Динамика углерода — {aoi_name}",
        markers=True,
    )
    fig.update_traces(
        line=dict(color="#52b788", width=3),
        marker=dict(size=10, color="#95d5b2",
                    line=dict(color="#081c15", width=1.5)),
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8f5e9", size=14),
        title_font=dict(color="#b7e4c7", size=18),
        xaxis_title="Год",
        yaxis_title="т C/га",
        margin=dict(l=20, r=20, t=60, b=20),
    )
    fig.update_xaxes(gridcolor="rgba(149,213,178,0.1)")
    fig.update_yaxes(gridcolor="rgba(149,213,178,0.15)")
    return fig