import unittest
from unittest import TestCase
from data.data import read_table,prepare_data
import pandas as pd

from sqlalchemy import create_engine

# créer une base de données
engine = create_engine('sqlite:///', echo=False)


class Test(TestCase):
    # remplir la base de données de tables
    def setUp(self):
        df5 = pd.DataFrame({"id": [1, 2, 3, 4], "date": ["2021-01-01 16:13:50", "2021-01-02 16:13:50",
                                                         "2021-01-03 16:13:50", "2021-01-04 16:13:50"],
                            "haineux": [True, True, True, True]})
        df5.to_sql('corpus_test', index=False, con=engine)
        df1 = pd.DataFrame({"id_type": [1, 2, 3, 4], "nom_type": ["racisme", "mysoginie", "homophobie", "validisme"]})
        df1.to_sql('type_test', index=False, con=engine)
        df2 = pd.DataFrame({"id": [1, 2, 3, 4], "id_type": [1, 2, 3, 4]})
        df2.to_sql('possede_test', index=False, con=engine)
        df3 = pd.DataFrame({"id_mot_clé": [1, 2, 3, 4], "mot": ["beur", "pute", "pd", "mongol"]})
        df3.to_sql('mot_test', index=False, con=engine)
        df4 = pd.DataFrame({"id": [1, 2, 3, 4], "id_mot_clé": [1, 2, 3, 4]})
        df4.to_sql('contient_test', index=False, con=engine)


    def test_get_dic(self):
        liste = ['corpus_test','possede_test', 'type_test','contient_test','mot_test']
        results = read_table(liste, con=engine)
        self.assertIsInstance(results,dict)


    def test_faillure_dic(self):
        liste = ['corpus_tes','possede_test', 'type_test','contient_test','mot_test']
        results = read_table(liste, con=engine)
        res= "la table corpus_tes n'existe pas"
        self.assertEqual(results, res)

    def test_get_df(self):
        liste = ['corpus_test','possede_test', 'type_test','contient_test','mot_test']
        res = read_table(liste, con=engine)
        results= prepare_data(res, liste)
        df = pd.DataFrame({"id": [1, 2, 3,4], "id_type": [1, 2, 3,4],
                         "date": ['2021-01-01 16:00:00', '2021-01-02 16:00:00', '2021-01-03 16:00:00','2021-01-04 16:00:00'],
                         "haineux":[True, True, True, True],
                         "nom_type":["racisme", "mysoginie", "homophobie", "validisme"],
                        "id_mot_clé":[1, 2, 3,4], "mot":["beur", "pute", "pd", "mongol"]})
        df['date'] = pd.to_datetime(df['date'].map(lambda t: t[:-6]), errors='coerce')
        df.set_index('date', drop=False, inplace=True)
        pd.testing.assert_frame_equal(results, df)

    def test_get_error(self):
        liste = ['corpus', 'possede_test', 'type_test', 'contient_test', 'mot_test']
        res = read_table(liste, con=engine)
        results = prepare_data(res, liste)
        err = "la table corpus n'existe pas"
        self.assertEqual(results, err)

    # supprimmer les tables à chaque fin de test
    def tearDown(self):
        engine.execute("DROP TABLE corpus_test")
        engine.execute("DROP TABLE type_test")
        engine.execute("DROP TABLE contient_test")
        engine.execute("DROP TABLE possede_test")
        engine.execute("DROP TABLE mot_test")

if __name__ == '__main__':
    unittest.main()