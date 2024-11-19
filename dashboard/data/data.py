import pandas as pd


# table list
table_liste = ['messages', 'possede', 'type', 'contient','mot_clé']


def read_table(liste,con):
    dic ={}
    # read each table in the bdd
    for table in liste:
        try:
            dic[table] = pd.read_sql_table(table, con)
        except ValueError:
            return "la table %s n'existe pas" %table
    return dic


def prepare_data(dic, liste):
    if dic and isinstance(dic,dict):
        try:
            # merge tables
            df = pd.merge(dic[liste[1]], dic[liste[0]][['id', 'date', 'haineux']], on="id")
            df = pd.merge(df, dic[liste[2]], on="id_type")
            df = pd.merge(df, dic[liste[3]], on="id")
            df = pd.merge(df, dic[liste[4]], on="id_mot_clé")
            # convert the column date to datetime format
            df['date'] = pd.to_datetime(df['date'].map(lambda t: t[:-6]), errors='coerce')
            # set date column as index
            df.set_index('date', drop=False, inplace=True)
            return df
        except KeyError:
            return "problème de nom des colonnes"
    else:
        return dic


