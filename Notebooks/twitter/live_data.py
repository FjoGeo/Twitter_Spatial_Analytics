# Erste Seite der Anwendung

import plotly.express as px
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input, State
from shapely.geometry import Point
from geopy.geocoders import Nominatim
import pandas as pd
import geopandas as gpd
from app import app, api

# API zur Konventierung, alternativ Google oder Yandex verwenden
app_geo = Nominatim(user_agent="tutorial")


# GeoCoder
# 2 Funktionen um den Standort zu einer Punktgeometrie zu konventieren
# Alternativ mit der Lambda Funktion von Python
def f_lat(dataframe):
    try:
        location = app_geo.geocode(dataframe['location'])
        return location[1][0]
    except:
        return 0.0


def f_lon(dataframe):
    try:
        location = app_geo.geocode(dataframe['location'])
        return location[1][1]
    except:
        return 0.0


# Layout der ersten Seite. Aufgeteilt in Zeilen und Spalten
# 1x Row hat beliebig viele Col
# html und CSS Elemente in der Col (Eingabe, Ausgabe, Button, Tabellen)
live_layout = html.Div([
    dbc.Row([
        dbc.Col([html.Label("Anzahl Ergebnisse"), dcc.Dropdown(id="resultz", multi=False, value=4, options=[
            {"label": "1", "value": 1},
            {"label": "2", "value": 2},
            {"label": "3", "value": 3},
            {"label": "4", "value": 4},
            {"label": "5", "value": 5},
            {"label": "6", "value": 6},
            {"label": "7", "value": 7},
            {"label": "8", "value": 8},
            {"label": "9", "value": 9},
            {"label": "10", "value": 10},
            {"label": "100", "value": 100},
            {"label": "alle", "value": 1_000_000},
        ], clearable=False, ), ], width=3, ),

        dbc.Col([html.Label("Anfang (Jahr)"), dcc.Dropdown(id="jahrz", multi=False, value=2016, options=[
            {"label": "2016", "value": 2016},
            {"label": "2017", "value": 2017},
            {"label": "2018", "value": 2018},
            {"label": "2019", "value": 2019},
            {"label": "2020", "value": 2020},
            {"label": "2021", "value": 2021},
            {"label": "2022", "value": 2022},
        ], clearable=False, ), ], width=3, ),

        dbc.Col([html.Label("Anfang (Monat)"), dcc.Dropdown(id="monatz", multi=False, value=1, options=[
            {"label": "1", "value": 1},
            {"label": "2", "value": 2},
            {"label": "3", "value": 3},
            {"label": "4", "value": 4},
            {"label": "5", "value": 5},
            {"label": "6", "value": 6},
            {"label": "7", "value": 7},
            {"label": "8", "value": 8},
            {"label": "9", "value": 9},
            {"label": "10", "value": 10},
            {"label": "11", "value": 11},
            {"label": "12", "value": 12},
        ], clearable=False, ), ], width=3, ),

        dbc.Col(
            [html.Label("Thematik (ohne '#')"),
             dcc.Input(id="input-handle", type="text", placeholder="Thema", value="Disaster", ), ], width=3, ), ],
        className="mt-4",
    ),
    dbc.Row([
        dbc.Col([html.Label("Ende (Jahr)"), dcc.Dropdown(id="jahr_ende", multi=False, value=2022, options=[
            {"label": "2016", "value": 2016},
            {"label": "2017", "value": 2017},
            {"label": "2018", "value": 2018},
            {"label": "2019", "value": 2019},
            {"label": "2020", "value": 2020},
            {"label": "2021", "value": 2021},
            {"label": "2022", "value": 2022},
        ], clearable=False, ), ], width={'size': 3, 'offset': 3}, ),

        dbc.Col([html.Label("Ende (Monat)"), dcc.Dropdown(id="monat_ende", multi=False, value=12, options=[
            {"label": "1", "value": 1},
            {"label": "2", "value": 2},
            {"label": "3", "value": 3},
            {"label": "4", "value": 4},
            {"label": "5", "value": 5},
            {"label": "6", "value": 6},
            {"label": "7", "value": 7},
            {"label": "8", "value": 8},
            {"label": "9", "value": 9},
            {"label": "10", "value": 10},
            {"label": "11", "value": 11},
            {"label": "12", "value": 12},
        ], clearable=False, ), ], width=3, ),
    ], ),

    dbc.Row([
        dbc.Col([
            html.Button(id="hit-button", children="Suche starten", 
                        style={"background-color": "black", "color": "white", "height": "50px", "width": "120px", "border-radius": "4px"}, )],
            width={'size': 1, 'offset': 5}, 
        )],
        className="mt-2", ),

    dbc.Row([
        dbc.Col([dcc.Graph(id="live_map", figure={})], width=12),
    ]),

    dbc.Row([
        dbc.Col([dcc.Graph(id="myscatter", figure={})], width=6),
        dbc.Col([dcc.Graph(id="myscatter2", figure={})], width=6),
    ]),
])


# callback Funktion, Reihenfolge beachten!
# component_id darf nicht identisch mit anderen sein, auch nicht in anderen Skripten
@app.callback(
    Output(component_id="live_map", component_property="figure"),
    Output(component_id="myscatter", component_property="figure"),
    Output(component_id="myscatter2", component_property="figure"),
    Input(component_id="hit-button", component_property="n_clicks"),
    State(component_id="resultz", component_property="value"),
    State(component_id="jahrz", component_property="value"),
    State(component_id="monatz", component_property="value"),
    State(component_id="jahr_ende", component_property="value"),
    State(component_id="monat_ende", component_property="value"),
    State(component_id="input-handle", component_property="value"),
)
def display_value(_, anzahl, jahr, monat, jahr_e, monat_e, suche):
    """
    Funktion sendet Request an Twitter, Antwort wird zu einem DataFrame verarbeitet
    --------------------------------------------
    anzahl: Anzahl der Ergebnisse, die dargestellt werden soll
    jahr: Anfangsdatum
    monat: Anfangsdatum
    jahr_e: Enddatum
    monat_e: Enddatum
    suche: Suchwort ohne '#'
    --------------------------------------------
    Output: Karte (plotly scatter_geo) und Balkendiagramme (plotly bar)
    """

    # Query: Für klammern und Leerzeichen HTML - URL Encoding
    # https://www.tutorialspoint.com/html/html_url_encoding.htm
    results = api.GetSearch(
        raw_query=f"q=%3A%23{suche}%3A%20until%3A{jahr_e}-{monat_e}-31%20since%3A{jahr}-{monat}-01&src=typed_query&count={anzahl}")

    twt_followers, twt_likes, twt_count, twt_friends, twt_name, twt_location, twt_text = [], [], [], [], [], [], []  # leere listen
    twt_retweet_count, twt_created_at = [], []

    # Es gibt Informationen über User und über die Nachricht
    for line in results:
        twt_likes.append(line.user.favourites_count)
        twt_followers.append(line.user.followers_count)
        twt_count.append(line.user.statuses_count)
        twt_friends.append(line.user.friends_count)
        twt_name.append(line.user.screen_name)
        twt_location.append(line.user.location)
        twt_text.append(line.text)
        twt_retweet_count.append(line.retweet_count)
        twt_created_at.append(line.created_at)

    # Dictionary für die Umwandlung in ein Pandas-DataFrame
    d = {
        "followers": twt_followers,
        "likes": twt_likes,
        "tweets": twt_count,
        "friends": twt_friends,
        "name": twt_name,
        "location": twt_location,
        "text": twt_text,
        "created": twt_created_at,
        "retweets": twt_retweet_count,
    }

    # DataFrame erstellen und bearbeiten
    df = pd.DataFrame(d)

    # Speicher als *.csv, nicht für den User sichtbar / kein Zugriff
    try:
        df.drop(columns='Unnamed: 0', inplace=True)
    except:
        pass
    df.to_csv('./live_twitter.csv')

    # GeoDataFrame aus der *.csv,
    gdf = gpd.read_file('./live_twitter.csv')
    gdf = gdf[gdf['location'] != '']
    gdf.reset_index(drop=True, inplace=True)
    gdf['lat'] = gdf.apply(f_lat, axis=1)
    gdf['lon'] = gdf.apply(f_lon, axis=1)
    gdf['geometry'] = [Point(xy) for xy in zip(gdf.lat, gdf.lon)]

    # Karte mit Hilfe von Plotly Express
    # Andere Darstellungen benötigen npm und javascript
    live_fig = px.scatter_geo(gdf,
                              projection="natural earth",
                              lat=gdf.geometry.x,
                              lon=gdf.geometry.y,
                              width=1300,
                              height=600,
                              color='location',
                              template="plotly_dark",
                              hover_name="text",
                              hover_data={'name': False, 'location': False}, )

    likes_fig = px.bar(gdf, x="location", y="likes", color='location',
                       hover_data={"text": False}, template="plotly_dark")

    retweet_fig = px.bar(gdf, x="location", y="retweets", color='location',
                         hover_data={"text": False}, template="plotly_dark")

    return live_fig, likes_fig, retweet_fig
