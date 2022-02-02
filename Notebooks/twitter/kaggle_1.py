# Darstellung eines Datensets von Kaggle
# https://www.kaggle.com/szelee/disasters-on-social-media

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import geopandas as gpd
from wordcloud import WordCloud
from app import app
import nltk

# Token für Plotly
mapbox_token = 'sk.eyJ1Ijoiam9lcm9nYW4iLCJhIjoiY2t2YjlkdXRkNDhuODJwcXdyYzFzc2E3NSJ9.ehtNyGFXLfOCS5HRA61brA'

# Import der Kaggle Daten
gdf = gpd.read_file('../../Data/twitter.geojson')

# Optionen für die Wordcloud
# https://www.udemy.com/course/python-data-science-machine-learning-bootcamp/
stopwords = nltk.corpus.stopwords.words('english')
stopwords = set(stopwords)
stopwords.update(["https", "http"])

# Einfaches Layout, strukturiert nach Zeilen und Spalten
# enthält Disaster, Länder, Karte und Wordcloud und Sunburst-chart
test_layout = html.Div([
    dbc.Row([
        dbc.Col(
            html.Label("Disaster:", style={'fontSize': 30, 'textAlign': 'center'}),
            width={'size': 3, 'offset': 1}),
        dbc.Col(
            html.Label("Location:", style={'fontSize': 30, 'textAlign': 'center'}),
            width={'size': 6, 'offset': 0}),
        dbc.Col(
            html.Label("Date:", style={'fontSize': 30, 'textAlign': 'center'}),
            width={'size': 2, 'offset': 0}),
    ]),

    dbc.Row([
        dbc.Col(
            dcc.Dropdown(id='disaster-dpdn',
                         options=[{'label': s, 'value': s} for s in sorted(gdf.disaster.unique())],
                         value='ablaze',
                         clearable=False
                         , style={'background-color': '#75F', 'color': '#000'}),
            width={'size': 3, "offset": 1, 'order': 1}
        ),
        dbc.Col(
            dcc.Dropdown(id='location-dpdn',
                         options=[],
                         multi=True,
                         style={'background-color': '#000', 'color': '#000'}
                         ),
            width={'size': 6, "offset": 0, 'order': 2}
        ),
        # Auswahl eines einzelnen Datums
        dbc.Col(
            dcc.DatePickerSingle(id='date-picker-single',
                                 date=gdf['timestamp'][0],
                                 min_date_allowed=gdf['timestamp'].iloc[0],
                                 max_date_allowed=gdf['timestamp'].iloc[-1],
                                 style={'background-color': '#75F', 'color': '#000'}
                                 ), width={'size': 2, "offset": 0, 'order': 3}),
    ]),

    dbc.Row([
        dbc.Col(
            dcc.Graph(id='display-map', figure={}),
            width={'size': 'max', "offset": 0}, ),
    ]),

    dbc.Row([
        dbc.Col(
            dcc.Graph(id='sun_burst', figure={}), width=6, ),
        dbc.Col(
            dcc.Graph(id='sun_burst2', figure={}), width=6, )
    ])

])


# 2 callback Funktionen, füllt Dropdown mit Katastrophen und daneben alle Orte
@app.callback(
    Output(component_id='location-dpdn', component_property='options'),
    Input(component_id='disaster-dpdn', component_property='value')
)
def set_location(disaster_opt):
    dff = gdf[gdf.disaster == disaster_opt]
    return [{'label': c, 'value': c} for c in sorted(dff.location.unique())]


@app.callback(
    Output(component_id='location-dpdn', component_property='value'),
    Input(component_id='location-dpdn', component_property='options')
)
def set_disaster(available_options):
    return [x['value'] for x in available_options]


# callback für das Update der Karte und der Diagramme/Darstellungen
@app.callback(
    Output(component_id='display-map', component_property='figure'),
    Output(component_id='sun_burst', component_property='figure'),
    Output(component_id='sun_burst2', component_property='figure'),
    Input(component_id='location-dpdn', component_property='value'),
    Input(component_id='disaster-dpdn', component_property='value'),
    Input(component_id='date-picker-single', component_property='date')
)
def update_graph_2(location, selected, date):
    if len(location) == 0:
        return dash.no_update
    else:
        dff = gdf[(gdf.disaster == selected) & (gdf.location.isin(location))]
        dff = dff[dff['timestamp'] > date]
        px.set_mapbox_access_token(mapbox_token)

        # Karte
        fig1 = px.scatter_geo(dff,
                              lat=dff.geometry.x,
                              lon=dff.geometry.y,
                              color="location",
                              width=1400,
                              height=600,
                              labels={},
                              template="plotly_dark",
                              scope="world",
                              hover_data={'disaster': False},
                              hover_name="text")

        # Sunburst
        fig2 = px.sunburst(dff[dff['confidence'] > 0.7], path=['disaster', 'choose_one', 'location'],
                           values='confidence',
                           color="confidence", template="plotly_dark")

        # Wordcloud
        text = dff.text.values
        wordcloud = WordCloud(width=1400, height=800, background_color='black', stopwords=stopwords).generate(str(text))
        fig_wordcloud = px.imshow(wordcloud, template="plotly_dark")
        fig_wordcloud.update_layout(margin=dict(l=20, r=20, t=30, b=20))
        fig_wordcloud.update_xaxes(visible=False)
        fig_wordcloud.update_yaxes(visible=False)

        return fig1, fig2, fig_wordcloud
