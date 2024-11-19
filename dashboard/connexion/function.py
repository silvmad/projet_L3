from flask_sqlalchemy import SQLAlchemy
import dash
import dash_bootstrap_components as dbc
from flask import Flask


# using flask server for bdd
server = Flask(__name__)


# declare the app
app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.CYBORG],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}],
                suppress_callback_exceptions=True)
app.title = "twitter dash_hate"

# sqlalchemy configuration
app.server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.server.config['SQLALCHEMY_ECHO'] = False

# load the parameters of connexion from config.sys


def load_config(file):
    dic = {}
    with open(file, 'r') as flux:
        load = flux.readlines()
        for ligne in load:
            conf = ligne.replace("\n", "")
            conf = conf.split("\t")
            try:
                dic[conf[0]] = conf[1]
            except IndexError:
                print("problème de lecture")
    if dic:
        return dic
    else:
        print("le fichier est vide")


# connexion to the BDD
def connexion_db(user,mdp, host, bdd):
    app.server.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://%s:%s@%s/%s" % (user, mdp, host, bdd)
    db = SQLAlchemy(app.server)
    try:
        db.engine.connect()
        print("la connexion a réussi")
        return db.engine
    except:
        print("la connexion a echoue")















