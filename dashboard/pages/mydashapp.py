from dash.dependencies import Output, Input
from dash.exceptions import PreventUpdate
from wordcloud import WordCloud
import plotly.express as px
import pandas as pd
from sqlalchemy import exc

import base64
from io import BytesIO

from data.data import table_liste,read_table,prepare_data
from connexion.init_conn import app,con
from pages.dashcard import *


# dashboard layout
# ************************************************************************
layout = dbc.Container([

    dbc.Row([
        dbc.Col([card_calender], xs=12, sm=12, md=12, lg=12, xl=12),
    ]),
    dbc.Row([
        dbc.Col([card_graphique], xs=12, sm=12, md=12, lg=12, xl=12),

    ]),
    dbc.Row([
        dbc.Col([card_pie], xs=12, sm=12, md=12, lg=4, xl=4),
        dbc.Col([card_img], xs=12, sm=12, md=12, lg=4, xl=4),
        dbc.Col([card_hist], xs=12, sm=12, md=12, lg=4, xl=4),

    ], no_gutters=False, justify='around'
    ),
    dcc.Interval(id='interval_pg', interval=300000, n_intervals=0),  # activated every 5min or when page refreshed
    # dcc.Store inside the app that stores the sharing data
    dcc.Store(id='stockmemo'),
], fluid=True)


# Callback section: connecting the components
# ************************************************************************
# filter data according to the user choices of date interval
# store data in stockmemo
@app.callback(Output('stockmemo', 'mydata'),
              [
                  Input('my-calender', 'start_date'),
                  Input('my-calender', 'end_date'),
                  Input('interval_pg','n_intervals')
              ])
def update_data(start_date, end_date,n):
    try:
        dff = prepare_data(read_table(table_liste,con),table_liste)
        if isinstance(dff,str) :
            print(dff)
            return
        if dff.empty:
            print("les tables sont vides pour le moment")
            return
        else:
            if (not start_date) and (not end_date):
                # Return all the rows on initial load.
                return dff.to_dict('records')
            dfm = dff.sort_index().loc[start_date:end_date]
            if dfm.empty:
                return dff.to_dict('records')
            return dfm.to_dict('records')
    except (exc.ArgumentError, NotImplementedError):
        print("revoir les paramètres de connexion")



# share data with dropdowns and generate their options
@app.callback(
    [

        Output('menu_line', 'options'),
        Output('menu_pie', 'options'),
        Output('menu_hist', 'options'),

    ],
    Input('stockmemo', 'mydata'),
)
def update_date_dropdown(data):
    if data is None:
        raise PreventUpdate
    dff = pd.DataFrame.from_dict(data)
    option1 = [{'label': x, 'value': x} for x in sorted(dff['nom_type'].unique())]
    option2 = [{'label': x, 'value': x} for x in sorted(dff['nom_type'].unique())]
    option3 = [{'label': x, 'value': x} for x in sorted(dff['mot'].unique())]
    return option1, option2, option3


# pie chart
# use the data in stockmemo and return a pie chart figure according
# to the users choices in the dropdown
@app.callback(
    Output('mypie', 'figure'),
    [
        Input('stockmemo', 'mydata'),
        Input('menu_pie', 'value'),
    ]
)
def update_graph(data, nametype):
    if data is None:
        raise PreventUpdate
    # using the share date
    dff = pd.DataFrame.from_dict(data)
    # filter data according to the user choices
    dff = dff[dff['nom_type'].isin(nametype)]
    # use plotly express to generate the figure
    pifig = px.pie(dff, names='nom_type', hole=.5, labels={'nom_type': 'type de haine '},
                   template='plotly_dark'
                   )
    return pifig


# Histogram
# use the data in stockmemo and return an histogramme figure according
# to the users choices in the dropdown
@app.callback(
    Output('myhist', 'figure'),
    [
        Input('stockmemo', 'mydata'),
        Input('menu_hist', 'value'),
    ]

)
def update_graph(data, mots):
    if data is None:
        raise PreventUpdate
    # using the share data
    dff = pd.DataFrame.from_dict(data)
    # filter data according to the users choices
    dff = dff[dff['mot'].isin(mots)]
    # using plotly express to generate figure
    fighist = px.histogram(dff, x='mot',
                           labels={'mot': 'mot haineux '
                                   },
                           template='plotly_dark'
                           )
    return fighist


# line chart
# use the data in stockmemo and return a line chart figure according
# to the users choices in the dropdown
@app.callback(
    Output('line', 'figure'),
    [
        Input('stockmemo', 'mydata'),
        Input('menu_line', 'value'),
    ]

)
def update_graph(data, nametype):
    if data is None:
        raise PreventUpdate
    dff = pd.DataFrame.from_dict(data)
    dff = dff[dff['nom_type'].isin(nametype)]
    dfm = dff.groupby(['nom_type', 'date']).size().reset_index(name='count')
    # using plotly express to generate figure
    figln = px.line(dfm, x='date', y='count', color='nom_type',
                    labels={'date': '', 'count': 'nombre de mots haineux par type'},
                    template='plotly_dark'
                    )
    return figln


# calender
@app.callback(
    Output('calender', 'children'),
    [Input('my-calender', 'start_date'),
     Input('my-calender', 'end_date')])
def update_output(start_date, end_date):
    string_prefix = 'vous avez choisi: '
    if start_date is not None:
        start_date_object = dt.fromisoformat(start_date)
        start_date_string = start_date_object.strftime('%d %B, %Y')
        string_prefix = string_prefix + 'début de période: ' + start_date_string + ' | '
    if end_date is not None:
        end_date_object = dt.fromisoformat(end_date)
        end_date_string = end_date_object.strftime('%d %B, %Y')
        string_prefix = string_prefix + 'fin de période: ' + end_date_string
    if len(string_prefix) == len('vous avez choisi: '):
        return 'choisissez une date'
    else:
        return string_prefix


# ************************************************************************
# create the image of the wordcloud

def plot_wordcloud(data):
    d = {a: x for a, x in data.values}
    wc = WordCloud(background_color='black', width=380, height=380).generate_from_frequencies(frequencies=d)
    return wc.to_image()


# callback generating the url of the image
@app.callback(
    Output('wordcloud', 'src'),
    [
        Input('wordcloud', 'id'),
        Input('stockmemo', 'mydata'),
    ])
def make_image(b, data):
    if data is None:
        raise PreventUpdate
    # using the share data
    dff = pd.DataFrame.from_dict(data)
    # filter and prepare data
    dfm = dff.groupby('mot').size().reset_index(name='count')
    dfm = dfm[['mot', 'count']]
    img = BytesIO()
    # generating the image using the data
    plot_wordcloud(data=dfm).save(img, format='PNG')
    # return the url of the image
    return 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())

