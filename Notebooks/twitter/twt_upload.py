# Option für den Upload von Daten
# Tutorial: https://www.youtube.com/watch?v=6W4HpSI20NM

import base64
import io
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from live_data import f_lat, f_lon
from app import app

# https://dash.plotly.com/dash-core-components/upload
upload_layout = html.Div([
    dcc.Upload(
        id='up_down_up_down',
        children=html.Div([
            'Upload: ',
            html.A('Drag & Drop oder Klick')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        multiple=True
    ),

    html.Div(id='table__1'),
    html.Br(),
    html.Div(id='output__div'),
    html.Br(),
    html.Div(id='output__figure'),
])


def parse_contents(contents, filename):
    """
    Funktion zur Verarbeitung der eingefügten csv
    --------------------------------------------
    contents: csv Datei
    filename: Name der Datei
    --------------------------------------------
    Output:
        komplettes Layout mit Tabellen und weiteren Interaktionen
    """
    assert 'csv' in filename
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
    try:
        df.drop(columns='Unnamed: 0', inplace=True)
    except:
        pass
    df.to_csv('./temp.csv')  # zwischenspeichern, leichter für die Verarbeitung mit GeoPandas

    return html.Div([
        dbc.Row([
            dbc.Col(html.P('Uploaded File: ' + filename),
                    ),
        ]),

        dbc.Row([
            dbc.Col([
                html.P("X auswählen:"),
                dcc.Dropdown(id='x_data', options=[{'label': x, 'value': x} for x in df.columns]),
            ]),

            dbc.Col([
                html.P("Y auswählen:"),
                dcc.Dropdown(id='y_data', options=[{'label': x, 'value': x} for x in df.columns]),
            ]),
        ]),

        dbc.Row([
            dbc.Col(html.Br(), ),
        ]),

        dbc.Row([
            dbc.Col(
                html.Button(id="submit_button", children="Diagramm",
                            style={"background-color": "grey", "color": "white", "height": "50px", "width": "120px",
                                   "border-radius": "4px"}, ),
                width={'size': 1, 'offset': 0},
            ),
            dbc.Col(
                html.Button(id="show_figure_button", children="Karte",
                            style={"background-color": "grey", "color": "white", "height": "50px", "width": "120px",
                                   "border-radius": "4px"}, ),
                width={'size': 1, 'offset': 0},
            ),
        ]),

        dbc.Row([
            dbc.Col(html.Br(), ),
        ]),

        dbc.Row([
            dbc.Col(
                dt.DataTable(
                    data=df.to_dict('records'),
                    filter_action="native",
                    sort_action="native",
                    sort_mode="single",
                    column_selectable="multi",
                    page_action="native",
                    page_current=0,
                    style_data={
                        'whiteSpace': 'normal',
                        'height': 'auto',
                        'color': 'white',
                        'backgroundColor': 'rgb(30, 30, 30)',
                        'border': '1px solid grey'
                    },
                    style_header={
                        'color': 'red',
                        'fontWeight': 'bold',
                        'backgroundColor': 'rgb(30, 30, 30)',
                    },
                    columns=[{'name': i, 'id': i} for i in df.columns],
                    page_size=5),

            ),

        ]),
        # The dcc.Store component is used to store JSON data in the browser
        # https://dash.plotly.com/dash-core-components/store
        dcc.Store(id='s__data', data=df.to_dict('records')),
    ])


# erstellt automatisch die Tabelle nach Drag & Drop
@app.callback(Output(component_id='table__1', component_property='children'),
              Input(component_id='up_down_up_down', component_property='contents'),
              State(component_id='up_down_up_down', component_property='filename'))
def update_output(cont, name):
    if cont is not None:
        children = [parse_contents(c, n) for c, n in zip(cont, name)]
        return children


# erstellen eines Diagramms nach Auswahl von X und Y und 
@app.callback(Output(component_id='output__div', component_property='children'),
              Input(component_id='submit_button', component_property='n_clicks'),
              State(component_id='s__data', component_property='data'),
              State(component_id='x_data', component_property='value'),
              State(component_id='y_data', component_property='value'))
def make_graphs(submitted, s_data, x_data, y_data):
    if submitted is None:
        return dash.no_update
    else:
        bar_fig = px.bar(s_data,
                         x=x_data,
                         y=y_data,
                         template="plotly_dark",
                         labels={"likes": "Likes"}).update_layout(
            showlegend=False,
            xaxis={'categoryorder': 'total ascending'}).update_traces(hovertemplate="<b>%{y}</b>")

        return dcc.Graph(figure=bar_fig)


# erstellen einer Karte
# benötigt Spalte 'location'
@app.callback(Output(component_id='output__figure', component_property='children'),
              Input(component_id='show_figure_button', component_property='n_clicks'),
              State(component_id='s__data', component_property='data'))
def make_graphs(submitted, s__data):
    if submitted is None:
        return dash.no_update
    else:
        gdf = gpd.read_file('./temp.csv')
        gdf = gdf[gdf['location'] != '']
        gdf.reset_index(drop=True, inplace=True)
        gdf['lat'] = gdf.apply(f_lat, axis=1)
        gdf['lon'] = gdf.apply(f_lon, axis=1)
        gdf['geometry'] = [Point(xy) for xy in zip(gdf.lat, gdf.lon)]

        up_fig = px.scatter_geo(gdf,
                                projection="natural earth",
                                lat=gdf.geometry.x,
                                lon=gdf.geometry.y,
                                width=1300,
                                height=600,
                                color='location',
                                template="plotly_dark",
                                hover_name="text",
                                title="Your Uploaded File",
                                hover_data={'name': False, 'location': False}, )

        return dcc.Graph(figure=up_fig)
