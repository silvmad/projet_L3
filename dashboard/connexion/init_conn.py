from connexion.function import load_config, connexion_db,app

# load the config file
try:
    config = load_config("config")
    # for the layout testing
except FileNotFoundError:
    config = load_config("../config")


# extract the parameters of the connexion from the dictionary
HOST = config.get("Bdd_host")
USER = config.get("Bdd_login")
PASSWORD = config.get("Bdd_secret")
DATABASE = config.get("Bdd")

# connect to BDD
con = connexion_db(USER, PASSWORD, HOST, DATABASE)







