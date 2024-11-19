import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from datetime import datetime as dt
from datetime import date as d


card_calender = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H5(
                    "Choisissez une date de début et une date de fin:",
                    className="card-text",
                ),

                html.Div([dcc.DatePickerRange(
                    id='my-calender',
                    end_date_placeholder_text="date de fin",  # text that appears when no end date chosen
                    start_date_placeholder_text="date de début",  # text that appears when no start date chosen
                    display_format='D-M-Y',
                    first_day_of_week=1,  # Display of calendar when open (0 = sunday)
                    min_date_allowed=dt(2017, 8, 5),
                    max_date_allowed=dt(2022, 7, 25),
                    initial_visible_month=d.today(),
                ),
                    html.Div(id='calender'),
                ]),
            ]),

    ],
    color="light",   # https://bootswatch.com/default/ for more card colors
    inverse=True,   # change color of text (black or white)
    outline=False,  # True = remove the block colors from the background and header
)

card_graphique = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H5("Évolution des types de haines dans le temps", className="card-title"),
                dcc.Dropdown(id='menu_line', multi=True, value=['homophobie', 'racisme'],
                             options=[], placeholder="Selectionnez un type",
                             style={"color": "#000000"}
                             ),
                dcc.Graph(id='line', figure={})
            ]
        ),
    ],
    color="light",   # https://bootswatch.com/default/ for more card colors
    inverse=True,   # change color of text (black or white)
    outline=False,  # True = remove the block colors from the background and header
)

card_pie = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H5(
                    "Répartition par type de haine", className="card-title"),
                dcc.Dropdown(id='menu_pie', multi=True, value=['homophobie', 'racisme'], options=[],
                             style={"color": "#000000"}
                             ),
                dcc.Graph(id='mypie', figure={})
            ]
        ),
    ],
    color="light",   # https://bootswatch.com/default/ for more card colors
    inverse=True,   # change color of text (black or white)
    outline=False,  # True = remove the block colors from the background and header
)

card_hist = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H5(
                    "Répartition des mots haineux par nombre", className="card-title"),
                dcc.Dropdown(id='menu_hist', multi=True, value=['bougnoule', 'pd'], options=[],
                             style={"color": "#000000"}
                             ),
                dcc.Graph(id='myhist', figure={}),
            ]
        ),
    ],
    color="light",   # https://bootswatch.com/default/ for more card colors
    inverse=True,   # change color of text (black or white)
    outline=False,  # True = remove the block colors from the background and header
)

card_img = dbc.Card([
    dbc.CardBody(
            [
                html.H5("Nuage de mots haineux", className="card-title"),
            ]
    ),
    dbc.CardImg(id="wordcloud", title="Nuage de mots haineux",
                style=
                {
                    'width': '100%',
                    'height': '470px',
                    'textAlign': 'center',
                }
                ),
],
    color="light",  # https://bootswatch.com/default/ for more card colors
    inverse=True,   # change color of text (black or white)
    outline=False,  # True = remove the block colors from the background and header
)






