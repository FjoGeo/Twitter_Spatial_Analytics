import warnings

warnings.filterwarnings('ignore')
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input
from app import app

# CLayouts der anderen Dateien
from live_data import live_layout
from kaggle_1 import test_layout
from kaggle_2 import layout_k
from additional_data import add_data_layout
from twt_upload import upload_layout
from nltk_data import nltk_layout

# app tabs
# dash-bootstrap teilweise für Design
# https://dash-bootstrap-components.opensource.faculty.ai/docs/components/tabs/
app_tabs = html.Div(
    [
        dbc.Tabs(
            [
                dbc.Tab(label="Suche", tab_id="live_data", labelClassName="text-success font-weight-bold",
                        activeLabelClassName="text-danger"),
                dbc.Tab(label="Tabelle und Download", tab_id="tab_data", labelClassName="text-success font-weight-bold",
                        activeLabelClassName="text-danger"),
                dbc.Tab(label="NLTK", tab_id="nltk_tab", labelClassName="text-success font-weight-bold",
                        activeLabelClassName="text-danger"),
                dbc.Tab(label="Upload", tab_id="tab_upload", labelClassName="text-success font-weight-bold",
                        activeLabelClassName="text-danger"),
                dbc.Tab(label="Disaster aus Kaggle", tab_id="kaggle-1", labelClassName="text-success font-weight-bold",
                        activeLabelClassName="text-danger"),
                dbc.Tab(label="Weitere Disaster", tab_id="kaggle-2", labelClassName="text-success font-weight-bold",
                        activeLabelClassName="text-danger"),
            ],
            id="tabs",
            active_tab="nltk_tab",  # live_data
        ),
    ], className="mt-3"
)

# Layout besteht aus Überschrift und den Tabs
# der Rest wird aus weiteren Dateien geladen
app.layout = dbc.Container([
    dbc.Row(
        dbc.Col(html.H1("Twitter app", style={"textAlign": "center"}), width=12)),  # überschrift
    html.Hr(),  # horizontal line
    dbc.Row(
        dbc.Col(app_tabs, width=12), className="mb-3"),  # tabs von oben
    html.Div(id='cont', children=[])  # 'content von den anderen files
])


# callback wechselt zwischen den einzelnen Files
# Layouts der anderen werden nur bei Aufruf geladen
@app.callback(
    Output(component_id="cont", component_property="children"),
    [Input(component_id="tabs", component_property="active_tab")]
)
def switch_tab(tab_chosen):
    if tab_chosen == "live_data":
        return live_layout
    elif tab_chosen == "tab_data":
        return add_data_layout
    elif tab_chosen == "tab_upload":
        return upload_layout
    elif tab_chosen == "kaggle-1":
        return test_layout
    elif tab_chosen == "kaggle-2":
        return layout_k
    elif tab_chosen == "nltk_tab":
        return nltk_layout
    return html.P("Hier kommt noch was rein...")


app.run_server(debug=True, port='8070')
