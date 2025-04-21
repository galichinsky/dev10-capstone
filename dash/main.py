import pandas as pd
from dash import Dash, dash_table, html, dcc, callback, Input, Output
import plotly.express as px
from sqlalchemy import create_engine
from dynaconf import Dynaconf


def build_engine():
    settings = Dynaconf(envvar_prefix="DB", load_dotenv=True)
    return create_engine(settings.ENGINE_URL, echo=False)

engine = build_engine()

query = """
select *
from country c
join quality q on q.country_id = c.country_id
join happiness h on h.country_id = c.country_id
order by h.happiness desc;
"""

df_quality = pd.read_sql(query, engine)

app = Dash(__name__)

def render_tab1():
    return html.Div(
        [
            dash_table.DataTable(
                data=df_quality.to_dict("records"), page_size=10, sort_action="native"
            ),
            # html.Label("Select a Year"),
            # dcc.Dropdown(
            #     id="year-dropdown1",
            #     options=[
            #         {"label": year, "value": year}
            #         for year in df_idb["year"].unique()
            #     ],
            #     value=df_idb["year"].max(),  # Default value
            # ),
            # dcc.Graph(id="choropleth-map"),
            # dcc.Graph(id="geo-map"),
            # dcc.Slider(
            #     id="year-slider",
            #     min=df_idb["year"].min(),
            #     max=df_idb["year"].max(),
            #     value=df_idb["year"].max(),
            #     marks={
            #         year: str(year)
            #         for year in range(df_idb["year"].min(), df_idb["year"].max() + 1, 5)
            #     },
            #     step=None,
            # ),
        ],
        style={"width": "auto", "margin": "auto"},
    )
    
app.layout = html.Div(
    [
        html.H1("International Database", style={"textAlign": "center"}),
        dcc.Tabs(
            [
                dcc.Tab(render_tab1(), label="World Data"),
                # dcc.Tab(render_tab2(), label="Country Data"),
                # dcc.Tab(render_tab3(), label="Multi-Country Comparisons"),
            ]
        ),
        # dcc.Interval(
        #     id="interval-component",
        #     interval=1000,
        #     n_intervals=0,
        # ),
    ]
)

def run_dash():
    app.run(debug=True)
    
if __name__ == "__main__":
    run_dash()