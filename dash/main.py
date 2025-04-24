import pandas as pd
from dash import Dash, dash_table, html, dcc, callback, Input, Output
import plotly.express as px
from sqlalchemy import create_engine
from dynaconf import Dynaconf
import statsmodels.api as sm

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

def render_all_data_tab():
    correlation_df = df_life[
        [
            "qol_index", "stability", "rights", "health", "safety", "climate", 
            "costs", "popularity", "happiness", "log_gdp", "social_support", 
            "healthy_life_expectancy", "freedom", "generosity", 
            "perceptions_of_corruption"
        ]
    ]
    
    df_life_table = df_life[[
        "country_name", "region", "qol_index", "stability", "rights",
        "health", "safety", "climate", "costs", "popularity", "happiness",
        "log_gdp", "social_support", "healthy_life_expectancy", "freedom",
        "generosity", "perceptions_of_corruption"
    ]]
    
    correlation_matrix = correlation_df.corr()

    # Create a heatmap for the correlation matrix
    fig = px.imshow(
        correlation_matrix,
        text_auto=True,
        # title="Correlation Matrix of Life Factors",
        labels={"color": "Correlation"},
    )
    
    return html.Div(
        [
            # html.H3("Life Data Table", style={"textAlign": "center"}),
            dash_table.DataTable(
            data=df_life_table.to_dict("records"),
            page_size=6,
            sort_action="native",
            style_table={
                "width": "100%",
                "margin": "auto",
                },
            style_cell={
                "textAlign": "left",
                "padding": "2px",
                "maxWidth": "50px",
                "whiteSpace": "normal",
            },
            ),
            html.H3("Correlation Matrix of Life Factors", style={"textAlign": "center", "marginBottom": "-10px"}),
            dcc.Graph(figure=fig, style={"width": "100%", "height": "1100px", "margin": "10px auto"}),
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
        title='Average Quality of Life Index by Region',
        labels={'value': 'Avg QOL Index', 'region': 'Region'},
    )
    fig1.update_layout(showlegend=False)
    
    fig2 = px.bar(
        regional_summary,
        x='region',
        y=['avg_happiness'],
        barmode='group',
        title='Average Happiness Score by Region',
        labels={'value': 'Avg Happiness Score', 'region': 'Region'},
        color_discrete_sequence=['red']
    )
    fig2.update_layout(showlegend=False)

    return html.Div(
        [
            # html.H3("Regional Trends in Quality of Life and Happiness", style={"textAlign": "center", "margin": "10px"}),
            html.Div(
                [
                    dcc.Graph(figure=fig1, style={"width": "50%", "margin": "10px"}),
                    dcc.Graph(figure=fig2, style={"width": "50%", "margin": "10px"}),
                ], 
                style={"display": "flex", "justify-content": "space-between", "margin-top": "60px"},
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
        # title='Relationship Between GDP (log_gdp) and Quality of Life (qol_index)',
        labels={'log_gdp': 'Log GDP', 'qol_index': 'Quality of Life Index'},
        trendline='ols'
    )
    fig.update_layout(
        showlegend=True  # Ensure the legend is displayed
    )

    return html.Div(
        [
            html.H3("GDP vs Quality of Life", style={"textAlign": "center", "margin-top": "30px"}),
            dcc.Graph(figure=fig, style={"margin": "auto", "width": "90%"}),
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
    
# Define predictors and target
X = df_life[["stability", "rights", "health", "safety", "costs", 
            "log_gdp", "social_support", 
            "healthy_life_expectancy", "freedom", "perceptions_of_corruption"]]
y_happiness = df_life["happiness"]
y_qol = df_life["qol_index"]

# Add a constant for the regression model
X = sm.add_constant(X)

# Fit regression models
model_happiness = sm.OLS(y_happiness, X).fit()
model_qol = sm.OLS(y_qol, X).fit()

# Predicted values
df_life["predicted_happiness"] = model_happiness.predict(X)
df_life["predicted_qol"] = model_qol.predict(X)

# Calculate R² values for the models
r2_happiness = model_happiness.rsquared
r2_qol = model_qol.rsquared

# Print the R² values
print(f"R² for Happiness Model: {r2_happiness:.2f}")
print(f"R² for Quality of Life Model: {r2_qol:.2f}")

# Calculate residuals
df_life["happiness_residual"] = df_life["happiness"] - df_life["predicted_happiness"]
df_life["qol_residual"] = df_life["qol_index"] - df_life["predicted_qol"]

# Define thresholds for outliers (e.g., residuals > {thresh} standard deviations)
thresh = 2.5
happiness_threshold = thresh * df_life["happiness_residual"].std()
qol_threshold = thresh * df_life["qol_residual"].std()

# Identify outliers
happiness_outliers = df_life[
    (df_life["happiness_residual"].abs() > happiness_threshold)
]
qol_outliers = df_life[
    (df_life["qol_residual"].abs() > qol_threshold)
]

# Scatter plot for happiness
fig_happiness = px.scatter(
    df_life,
    x="predicted_happiness",
    y="happiness",
    color=df_life["happiness_residual"].abs() > happiness_threshold,
    title="Happiness: Actual vs Predicted",
    labels={"x": "Predicted Happiness", "y": "Actual Happiness"},
)
fig_happiness.add_shape(
    type="line",
    x0=df_life["predicted_happiness"].min(),
    y0=df_life["predicted_happiness"].min(),
    x1=df_life["predicted_happiness"].max(),
    y1=df_life["predicted_happiness"].max(),
    line=dict(color="Red", dash="dash"),
)
fig_happiness.update_layout(showlegend=False)

# Scatter plot for quality of life
fig_qol = px.scatter(
    df_life,
    x="predicted_qol",
    y="qol_index",
    color=df_life["qol_residual"].abs() > qol_threshold,
    title="Quality of Life: Actual vs Predicted",
    labels={"x": "Predicted QOL", "y": "Actual QOL"},
)
fig_qol.add_shape(
    type="line",
    x0=df_life["predicted_qol"].min(),
    y0=df_life["predicted_qol"].min(),
    x1=df_life["predicted_qol"].max(),
    y1=df_life["predicted_qol"].max(),
    line=dict(color="Red", dash="dash"),
)
fig_qol.update_layout(showlegend=False)

def render_outliers_tab():
    return html.Div(
        [
            html.H3("Outliers in Happiness and Quality of Life", style={"textAlign": "center"}),
            html.Div(
                [
                    html.H4("Happiness Outliers"),
                    dash_table.DataTable(
                        data=happiness_outliers.to_dict("records"),
                        page_size=5,
                        style_table={
                            "width": "100%",
                            "margin": "auto",
                        },
                        style_cell={
                            "textAlign": "left",
                            "padding": "2px",
                            "maxWidth": "50px",
                            "whiteSpace": "normal",
                        },
                    ),
                ]
            ),
            html.Div(
                [
                    html.H4("Quality of Life Outliers"),
                    dash_table.DataTable(
                        data=qol_outliers.to_dict("records"),
                        page_size=5,
                        style_table={
                            "width": "100%",
                            "margin": "auto",
                        },
                        style_cell={
                            "textAlign": "left",
                            "padding": "2px",
                            "maxWidth": "50px",
                            "whiteSpace": "normal",
                        },
                    ),
                ]
            ),
            html.Div(
                [
                    dcc.Graph(figure=fig_happiness, style={"width": "48%", "display": "inline-block", "margin": "10px"}),
                    dcc.Graph(figure=fig_qol, style={"width": "48%", "display": "inline-block", "margin": "10px"}),
                ],
                style={"display": "flex", "justify-content": "center"},
            ),
        ]
    ),
    
# QOL and happiness correlation
qol_happiness_corr = df_life[['qol_index', 'happiness']].corr().iloc[0, 1]
print(f"Correlation between Quality of Life and Happiness: {qol_happiness_corr:.2f}")

# Define predictors and target
X_qol = sm.add_constant(df_life["qol_index"])  # Add constant for intercept
y_happiness = df_life["happiness"]

# Fit the regression model
model_qol_happiness = sm.OLS(y_happiness, X_qol).fit()

# Get the R² value
r2_qol_happiness = model_qol_happiness.rsquared
print(f"R² value for Quality of Life vs Happiness: {r2_qol_happiness:.2f}")

# Create scatter plot with trendline
fig_qol_happiness = px.scatter(
    df_life,
    x="qol_index",
    y="happiness",
    title="Relationship Between Quality of Life and Happiness",
    labels={"qol_index": "Quality of Life Index", "happiness": "Happiness Score"},
    trendline="ols",  # Add regression trendline
    trendline_color_override="red",  # Make the trendline red for visibility
)

# Update layout for better visualization
fig_qol_happiness.update_layout(
    xaxis_title="Quality of Life Index",
    yaxis_title="Happiness Score",
    margin={"t": 50, "b": 50, "l": 50, "r": 50},
)

def render_qol_happiness_tab():
    return html.Div(
        [
            dcc.Graph(figure=fig_qol_happiness, style={"width": "90%", "margin": "auto"}),
        ]
    )

app.layout = html.Div(
    [
        html.H2("Quality of Life and Happiness", style={"textAlign": "center", "margin-left": "370px", "margin-top": "50px"}),
        html.Div(
            [
                html.Div(
                    dcc.Tabs(
                        id="tabs",
                        value="tab1",
                        children=
                        [
                            dcc.Tab(label="Data and Correlations", value="tab1"),
                            dcc.Tab(label="Regional Trends", value="tab2"),
                            dcc.Tab(label="GDP vs Quality of Life", value="tab3"),
                            dcc.Tab(label="Climate vs Quality of Life and Happiness", value="tab4"),
                            dcc.Tab(label="Social Support vs Happiness and Quality of Life", value="tab5"),
                            dcc.Tab(label="Outliers in Happiness and QOL", value="tab6"),
                            dcc.Tab(label="QOL vs Happiness", value="tab7"),
                        ],
                        vertical=True,  # Make tabs vertical
                        style={"height": "auto", "borderRight": "1px solid #ccc", "padding": "10px"},
                    ),
                    style={"flex": "0 0 auto", "display": "flex", "flexDirection": "column"},
                ),
                html.Div(
                    id="tab-content",
                    style={"flex": "1", "padding": "20px", "margin": "auto"},  # Content area styling
                ),
            ],
            style={"display": "flex"},
        ),
    ]
),
style={"width": "100%", "margin": "auto", "display": "flex", "flexDirection": "column"},


@callback(
    Output("tab-content", "children"),
    Input("tabs", "value"),
)
def update_tab_content(tab):
    if tab == "tab1":
        return render_all_data_tab()
    elif tab == "tab2":
        return render_regional_tab()
    elif tab == "tab3":
        return render_gdp_qol_tab()
    elif tab == "tab4":
        return render_climate_tab()
    elif tab == "tab5":
        return render_social_support_tab()
    elif tab == "tab6":
        return render_outliers_tab()
    elif tab == "tab7":
        return render_qol_happiness_tab()
    return html.Div("No content available")    

def run_dash():
    app.run(debug=True)
    
if __name__ == "__main__":
    run_dash()