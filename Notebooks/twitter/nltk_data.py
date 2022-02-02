# Bearbeitung der Tweets mit NLTK
# Tutorial: https://www.youtube.com/watch?v=MpIi4HtCiVk&list=LL&index=1
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import dash_bootstrap_components as dbc
from nltk.stem.snowball import SnowballStemmer
import pandas as pd
import re
import spacy
from app import app
# !python -m spacy download en_core_web_sm
# nltk.download('punkt')
# nltk.download('wordnet')
nlp = spacy.load('en_core_web_lg')


def start_nltk():
    """
    Funktion zur Verarbeitung von Tweets zu DataFrames mit NLTK
    Teilweise übernommen aus: https://github.com/AlexTheAnalyst/PythonCode/blob/master/Twitter%20Scraper%20V8.ipynb
    --------------------------------------------
    variables: None
    --------------------------------------------
    Output:
        df: DataFrame mit den häufigsten Wörtern
        df2: DataFrame mit den häufigsten Unternehmen
    """
    # DataFrame nur mit Tweets aus dem ersten Tab des Programms
    nltk_df = pd.read_csv('./live_twitter.csv') #'./live_twitter-Copy1.csv' zum testen mit 100 Tweets
    nltk_df = nltk_df[~nltk_df.text.str.contains("RT")]  # retweets löschen
    nltk_df = nltk_df.text

    # Aufteilen der Sätze in Wörter
    all_sentences = []
    for word in nltk_df:
        all_sentences.append(word)
    lines = list()
    for line in all_sentences:
        words = line.split()
        for w in words:
            lines.append(w)

    # Entfernen aller sonstigen Zeichen mit REGEX
    lines = [re.sub(r'[^A-Za-z0-9]+', '', x) for x in lines]
    lines2 = []
    for word in lines:
        if word != '':
            lines2.append(word)

    # SnowballStemmer entfernt Wörter mit dem gleichen Wortstamm
    # Sprache wird auf Englisch gestellt, da auch die Abfrage auf Englisch erfolgt
    s_stemmer = SnowballStemmer(language='english')
    stem = []
    for word in lines2:
        stem.append(s_stemmer.stem(word))

    # Stopwords wie 'a', 'the' usw. werden entfernt
    stem2 = []
    for word in stem:
        if word not in nlp.Defaults.stop_words:
            stem2.append(word)
    df = pd.DataFrame(stem2)
    df = df[0].value_counts()

    # Suche und Aufzählung von Unternehmen in Tweets --> zweiter DataFrame
    str1 = " "
    stem2 = str1.join(lines2)
    stem2 = nlp(stem2)
    label = [(X.text, X.label_) for X in stem2.ents]
    df2 = pd.DataFrame(label, columns=['Word', 'Entity'])
    df2 = df2.where(df2['Entity'] == 'ORG')
    df2 = df2['Word'].value_counts()

    return df, df2


# Einfaches Layout aus zwei Überschriften und zwei Diagrammen
nltk_layout = html.Div([
    dbc.Row([
        dbc.Col(
            html.H3('Häufigsten Wörter'), width={'size': 6, 'offset': 4},
        ),
    ]),
    dbc.Row([
        dbc.Col(
            html.Div(id='nltk_1'), width={'size': 10, 'offset': 1},
        ),
    ]),

    dbc.Row([
        dbc.Col(
            html.H3('Häufigsten Unternehmen'), width={'size': 6, 'offset': 4},
        ),
    ]),
    dbc.Row([
        dbc.Col(
            html.Div(id='nltk_2'), width={'size': 10, 'offset': 1},
        ),
    ]),

])


# Callback für das erste Diagramm
# wird automatisch beim start geladen
@app.callback(Output(component_id='nltk_1', component_property='children'),
              Input(component_id='nltk_1', component_property='children'))
def top_words_count(_):
    df, _ = start_nltk()
    df = df[:15, ]
    df.sort_values(ascending=True, inplace=True)
    fig = px.bar(df, x=df.values, y=df.index, color=df.values,
                 labels={'x': 'Anzahl der Wörter', 'index': 'Wörter aus Tweets'}, template="plotly_dark", height=500)

    return dcc.Graph(figure=fig)


# zweites Callback, für das zweite Diagramm
# verwendet plotly express bar, anstatt seaborn und matplotlib
@app.callback(Output(component_id='nltk_2', component_property='children'),
              Input(component_id='nltk_1', component_property='children'))
def top_company_count(_):
    try:
        _, df = start_nltk()
        df = df[:5, ]
        df.sort_values(ascending=True, inplace=True)
        fig = px.bar(df, x=df.values, y=df.index, color=df.values,
                     labels={'x': 'Anzahl der Wörter', 'index': 'Wörter aus Tweets'}, template="plotly_dark", height=500)
        
        return dcc.Graph(figure=fig)
    except:
        fig = []

    #return dcc.Graph(figure=fig)
