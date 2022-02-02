# Logindaten und stylesheet

import dash
import dash_bootstrap_components as dbc
import twitter

api = twitter.Api(consumer_key='-',
                      consumer_secret='-',
                      access_token_key='-',
                      access_token_secret='-')

app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.CYBORG],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )