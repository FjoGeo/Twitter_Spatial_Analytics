# Darstellung eines Datensets von Kaggle
# https://www.kaggle.com/frednavruzov/disaster-tweets-geodata/version/1

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import geopandas as gpd
from shapely.geometry import Point
from app import app

# Manche Darstellungen von Plotly benötigen ein Token
mapbox_token = 'sk.eyJ1Ijoiam9lcm9nYW4iLCJhIjoiY2t2YjlkdXRkNDhuODJwcXdyYzFzc2E3NSJ9.ehtNyGFXLfOCS5HRA61brA'

# Import der Geodaten mit GeoPandas
File_1 = '../../Data/geodata.csv'
df_1 = gpd.read_file(File_1)
df_1 = df_1[df_1['country'] != '']
df_1['lat'] = df_1['lat'].astype(float)
df_1['lon'] = df_1['lon'].astype(float)
df_1['geometry'] = [Point(xy) for xy in zip(df_1.lat, df_1.lon)]

# Einfaches Layout, strukturiert nach Zeilen und Spalten
# enthält Länder, Städte, Karte und Diagramm
layout_k = html.Div([
    dbc.Row([
        dbc.Col(
            html.Label("Country:", style={'fontSize': 30, 'textAlign': 'center'}),
            width={'size': 3, 'offset': 1}),
        dbc.Col(
            html.Label("City:", style={'fontSize': 30, 'textAlign': 'center'}),
            width={'size': 6, 'offset': 0}),
    ]),

    dbc.Row([
        dbc.Col(
            dcc.Dropdown(id='country-dpdn',
                         options=[{'label': s, 'value': s} for s in sorted(df_1.country.unique())],
                         value='DEU', clearable=False,
                         style={'background-color': '#75F', 'color': '#000'}),
            width={'size': 3, "offset": 1, 'order': 1}),

        dbc.Col(
            dcc.Dropdown(id='city-dpdn',
                         options=[],
                         multi=True,
                         style={'background-color': '#000', 'color': '#000'}),
            width={'size': 6, "offset": 0, 'order': 2}),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.Graph(id='display-map2', figure={}),
            width={'size': '8', "offset": 0}, ),
        dbc.Col(
            dcc.Graph(id='bar_plot', figure={}),
            width={'size': '4', "offset": 0}, ),
    ]),
])


# callback Funktion
# alle Städte eines ausgewählten Landes anzeigen
@app.callback(
    Output(component_id='city-dpdn', component_property='options'),
    Input(component_id='country-dpdn', component_property='value')
)
def set_cities(all_options):
    dff = df_1[df_1.country == all_options]
    return [{'label': c, 'value': c} for c in sorted(dff.city.unique())]


# callback Funktion für dropdown
# enthält alle Länder
@app.callback(
    Output(component_id='city-dpdn', component_property='value'),
    Input(component_id='city-dpdn', component_property='options')
)
def set_dropdown(options):
    return [x['value'] for x in options]


# callback für das Update der Karte und des Diagramms
@app.callback(
    Output(component_id='display-map2', component_property='figure'),
    Output(component_id='bar_plot', component_property='figure'),
    Input(component_id='city-dpdn', component_property='value'),
    Input(component_id='country-dpdn', component_property='value'),
)
def update_graph_1(selected_country, selected_city):
    if len(selected_country) == 0:
        return dash.no_update
    else:
        dff = df_1[(df_1.country == selected_city) & (df_1.city.isin(selected_country))]

        px.set_mapbox_access_token(mapbox_token)
        fig__1 = px.scatter_geo(dff,
                                projection="natural earth",
                                lat=dff.geometry.x,
                                lon=dff.geometry.y,
                                color='city',
                                template="plotly_dark",
                                hover_name="city",
                                center={'lat': dff.iloc[0].geometry.x, 'lon': dff.iloc[0].geometry.y},
                                # navigiert zum Land
                                hover_data={'country': False}, )

        df_stats = dff.copy()
        df_stats['count'] = 1
        df_stats = df_stats.groupby(by=['country', 'city']).sum()
        df_stats.reset_index(inplace=True)
        df_stats.sort_values(by=['count'], inplace=True, ascending=False)

        fig__2 = px.bar(df_stats, x='country', y='count', template="plotly_dark", color='city')

        return fig__1, fig__2
