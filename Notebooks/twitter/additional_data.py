# Tabelle mit Ergebnissen aus der Suche in 'live_data.py'

# Datatable https://dash.plotly.com/datatable
# https://dash.plotly.com/datatable/reference
# Vorlage: https://github.com/Coding-with-Adam/Dash-by-Plotly/blob/master/DataTable/datatable_intro_and_sort.py

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import dash_table as dt
from app import app
from dash_extensions.snippets import send_data_frame

# Import der Tabelle, die automatisch beim Aufrufen der ersten Seite erstellt wurde
df = pd.read_csv('./live_twitter.csv')
df.dropna(inplace=True)
df.drop(columns='Unnamed: 0', inplace=True)

# Das Layout, das aus einer Tabelle und einem Diagramm besteht
add_data_layout = html.Div([
    dbc.Row(
        dbc.Col(html.H3("Suchergebnis"),  # Titel
                width={'size': 6, 'offset': 4}, ),
    ),
    dbc.Row([
        dbc.Col(dt.DataTable(
            id='data_table',
            data=df.to_dict('records'),
            editable=True,
            filter_action="native",
            sort_action="native",
            sort_mode="single",
            column_selectable="multi",
            row_deletable=True,
            page_action="native",
            page_current=0,
            page_size=3,
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
            columns=[{"name": i, "id": i} for i in df.columns],
        ),
        ),

    ]),

    dbc.Row([
        dbc.Col(html.Br(), ),
    ]),

    # https://dash.plotly.com/dash-core-components/download
    dbc.Row([
        dbc.Col([html.Button("Download CSV", id="btn_csv",
                             style={"background-color": "black", "color": "white", "height": "50px", "width": "150px",
                                    "border-radius": "4px"}, ),
                 dcc.Download(id="download-dataframe-csv"), ], width={'size': 1, 'offset': 0}, ),

        dbc.Col([html.Button("Download Excel", id="btn_xlsx",
                             style={"background-color": "black", "color": "white", "height": "50px", "width": "150px",
                                    "border-radius": "4px"}, ),
                 dcc.Download(id="download-dataframe-xlsx"), ], width={'size': 2, 'offset': 1}, ), ]
    ),

    dbc.Row([
        dbc.Col(dcc.Graph(id='bar', figure={}),
                width={'size': 'max', "offset": 0},
                ),
    ]),
])


# callback für das Diagramm, welches automatisch aktualisiert wird bei Änderung der Tabelle
# callback kann direkt auf Parameter der Tabelle zugreifen
@app.callback(
    Output(component_id='bar', component_property='figure'),
    Input(component_id='data_table', component_property="derived_virtual_data")
)
def update__bar(complete_table):
    dff = pd.DataFrame(complete_table)

    if "location" in dff and "likes" in dff:
        bar_figure_1 = px.bar(
            data_frame=dff,
            x='location',
            y='likes',
            color='location',
            template="plotly_dark",
            labels={"likes": "Likes"}).update_layout(
            showlegend=False,
            xaxis={'categoryorder': 'total ascending'}).update_traces(hovertemplate="<b>%{y}</b>")

        return bar_figure_1


# callback für die Aktualisierung der Tabelle,
# die sonst nut beim Start geladen wird und nicht auf weitere Suchen reagiert
@app.callback(
    Output(component_id='data_table', component_property='data'),
    Input(component_id='data_table', component_property='editable')
)
def tabelle_neu_laden(_):
    temporal_df = pd.read_csv('./live_twitter.csv')
    temporal_df.dropna(inplace=True)
    temporal_df.drop(columns='Unnamed: 0', inplace=True)
    irgendwas = temporal_df.to_dict('records')

    return irgendwas


# callback für den Download der Tabelle
# offizielle Implementierung funktioniert nicht! (# https://dash.plotly.com/dash-core-components/download)
# Lösung auf Stackoverflow
# https://stackoverflow.com/questions/61784556/download-csv-file-in-dash
@app.callback(
    Output(component_id="download-dataframe-csv", component_property="data"),  # !!
    Input(component_id="btn_csv", component_property="n_clicks"),
    prevent_initial_call=True,
)
def func_1(n_clicks):
    temporal_df = pd.read_csv('./live_twitter.csv')
    temporal_df.dropna(inplace=True)
    try:
        temporal_df.drop(columns='Unnamed: 0', inplace=True)
    except:
        pass

    return send_data_frame(temporal_df.to_csv, "download.csv")


@app.callback(
    Output(component_id="download-dataframe-xlsx", component_property="data"),
    Input(component_id="btn_xlsx", component_property="n_clicks"),
    prevent_initial_call=True,
)
def func_2(n_clicks):
    temporal_df = pd.read_csv('./live_twitter.csv')
    temporal_df.dropna(inplace=True)
    try:
        temporal_df.drop(columns='Unnamed: 0', inplace=True)
    except:
        pass

    return send_data_frame(temporal_df.to_excel, filename="twitter.xlsx")
