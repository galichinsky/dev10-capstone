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
select 
    c.country_name,
    c.region,
    q.qol_index,
    q.stability,
    q.rights,
    q.health,
    q.safety,
    q.climate,
    q.costs,
    q.popularity,
    h.happiness,
    h.log_gdp,
    h.social_support,
    h.healthy_life_expectancy,
    h.freedom,
    h.generosity,
    h.perceptions_of_corruption
from country c
join quality q on q.country_id = c.country_id
join happiness h on h.country_id = c.country_id
order by q.qol_index desc;
"""

df_life = pd.read_sql(query, engine)

def get_regional_summary():
    regional_summary = df_life.groupby("region").agg(
        avg_qol_index=("qol_index", "mean"),
        avg_happiness=("happiness", "mean")
    ).reset_index()
    
    regional_summary = regional_summary.sort_values(by='avg_qol_index', ascending=False)
    return regional_summary

gdp_qol_corr = df_life[["log_gdp", "qol_index"]].corr().iloc[0, 1]
climate_qol_corr = df_life[['climate', 'qol_index']].corr().iloc[0, 1]
climate_happiness_corr = df_life[['climate', 'happiness']].corr().iloc[0, 1]
social_support_happiness_corr = df_life[['social_support', 'happiness']].corr().iloc[0, 1]
social_support_qol_corr = df_life[['social_support', 'qol_index']].corr().iloc[0, 1]

app = Dash(__name__)

def render_tab1():
    
    correlation_matrix = df_life[
        [
            "qol_index", "stability", "rights", "health", "safety", "climate", 
            "costs", "popularity", "happiness", "log_gdp", "social_support", 
            "healthy_life_expectancy", "freedom", "generosity", 
            "perceptions_of_corruption"
        ]
    ].corr()

    # Create a heatmap for the correlation matrix
    fig = px.imshow(
        correlation_matrix,
        text_auto=True,
        # title="Correlation Matrix of Life Factors",
        labels={"color": "Correlation"},
    )
    
    return html.Div(
        [
            html.H3("Life Data Table", style={"textAlign": "center"}),
            dash_table.DataTable(
                data=df_life.to_dict("records"),
                page_size=10,
                sort_action="native",
                style_table={"margin": "20px auto", "width": "90%"},
            ),
            html.H2("Correlation Matrix of Life Factors", style={"textAlign": "center", "marginTop": "0px"}),
            dcc.Graph(figure=fig, style={"width": "100%", "height": "1100px", "margin": "20px auto"}),
        ],
        style={"width": "100%", "margin": "auto"},
    ),
    
def render_regional_tab():
    # Get regional summary data
    regional_summary = get_regional_summary()

    # Create a bar chart for regional trends
    fig1 = px.bar(
        regional_summary,
        x='region',
        y=['avg_qol_index'],
        barmode='group',
        title='Average Quality of Life and Happiness Scores by Region',
        labels={'value': 'Avg QOL Index', 'region': 'Region'},
    )
    fig1.update_layout(showlegend=False)
    
    fig2 = px.bar(
        regional_summary,
        x='region',
        y=['avg_happiness'],
        barmode='group',
        title='Average Quality of Life and Happiness Scores by Region',
        labels={'value': 'Avg Happiness Score', 'region': 'Region'},
        color_discrete_sequence=['red']
    )
    fig2.update_layout(showlegend=False)

    return html.Div(
        [
            html.H3("Regional Trends in Quality of Life and Happiness", style={"textAlign": "center"}),
            html.Div(
                [
                    dcc.Graph(figure=fig1, style={"width": "50%", "display": "inline-block", "margin-left": "5px"}),
                    dcc.Graph(figure=fig2, style={"width": "50%", "display": "inline-block", "margin-right": "5px"}),
                ], 
                style={"display": "flex", "justify-content": "center"},
            ),
        ],
        style={"width": "100%", "margin": "auto"}
    ), 

def render_gdp_qol_tab():
    # Scatter plot for GDP vs Quality of Life
    fig = px.scatter(
        df_life,
        x='log_gdp',
        y='qol_index',
        title='Relationship Between GDP (log_gdp) and Quality of Life (qol_index)',
        labels={'log_gdp': 'Log GDP', 'qol_index': 'Quality of Life Index'},
        trendline='ols'
    )
    fig.update_layout(
        showlegend=True  # Ensure the legend is displayed
    )

    return html.Div(
        [
            html.H3("GDP vs Quality of Life", style={"textAlign": "center"}),
            dcc.Graph(figure=fig, style={"margin": "20px auto", "width": "90%"}),
        ]
    ),

def render_climate_tab():
    # Scatter plot for Climate vs Quality of Life
    fig1 = px.scatter(
        df_life,
        x='climate',
        y='qol_index',
        title='Relationship Between Climate and Quality of Life',
        labels={'climate': 'Climate Score', 'qol_index': 'Quality of Life Index'},
        trendline='ols'  # Add a trendline
    )

    # Scatter plot for Climate vs Happiness
    fig2 = px.scatter(
        df_life,
        x='climate',
        y='happiness',
        title='Relationship Between Climate and Happiness',
        labels={'climate': 'Climate Score', 'happiness': 'Happiness Score'},
        trendline='ols'  # Add a trendline
    )

    return html.Div(
        [
            html.H3("Impact of Environmental Factors on Well-Being", style={"textAlign": "center"}),
            html.Div(
                [
                    dcc.Graph(figure=fig1, style={"width": "48%", "display": "inline-block", "margin": "10px"}),
                    dcc.Graph(figure=fig2, style={"width": "48%", "display": "inline-block", "margin": "10px"}),
                ],
                style={"display": "flex", "justify-content": "center"},
            ),
        ],
        style={"width": "100%", "margin": "auto"}
    ),
    
def render_social_support_tab():
    # Scatter plot for Social Support vs Happiness
    fig1 = px.scatter(
        df_life,
        x='social_support',
        y='happiness',
        title='Relationship Between Social Support and Happiness',
        labels={'social_support': 'Social Support Score', 'happiness': 'Happiness Score'},
        trendline='ols'  # Add a trendline
    )

    # Scatter plot for Social Support vs Quality of Life
    fig2 = px.scatter(
        df_life,
        x='social_support',
        y='qol_index',
        title='Relationship Between Social Support and Quality of Life',
        labels={'social_support': 'Social Support Score', 'qol_index': 'Quality of Life Index'},
        trendline='ols'  # Add a trendline
    )

    return html.Div(
        [
            html.H3("Impact of Social Support on Well-Being", style={"textAlign": "center"}),
            html.Div(
                [
                    dcc.Graph(figure=fig1, style={"width": "48%", "display": "inline-block", "margin": "10px"}),
                    dcc.Graph(figure=fig2, style={"width": "48%", "display": "inline-block", "margin": "10px"}),
                ],
                style={"display": "flex", "justify-content": "center"},
            ),
        ],
        style={"width": "100%", "margin": "auto"}
    )
    
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
    # style={"width": "auto", "margin": "auto"}
    
app.layout = html.Div(
    [
        html.H2("Quality of Life and Happiness by Country", style={"textAlign": "center"}),
        dcc.Tabs(
            [
                dcc.Tab(render_tab1(), label="Data and Correlations"),
                dcc.Tab(render_regional_tab(), label="Regional Trends"),
                dcc.Tab(render_gdp_qol_tab(), label="GDP vs Quality of Life"),
                dcc.Tab(render_climate_tab(), label="Climate vs Quality of Life and Happiness"),
                dcc.Tab(render_social_support_tab(), label="Social Support vs Happiness and Quality of Life"),
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