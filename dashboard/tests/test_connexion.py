import unittest
from unittest import TestCase
from connexion.function import load_config, connexion_db
from unittest.mock import patch

class Test(TestCase):
    def test_load_config(self):
        dic = load_config("fixtures/configtest.sys")
        res = {'T_api_key': 'x',
                'T_api_secret': 'x',
                'T_api_token': 'x',
                'T_api_token_secret': 'x',
                'Bdd_host': 'localhost', 'Bdd_login': 'postgres', 'Bdd_secret': 'mdp',
                'Bdd': 'haine_base', 'Bdd_table': 'message', 'langue': 'fr',
                'nbre_tweet': '100', 'max_tweet': '500000', 'rate_limite': '450', 'interval': '900'}

        self.assertDictEqual(dic, res)

    @patch('builtins.print')
    def test_empty_dic(self,mock_print):
        load_config("fixtures/emptyfile")
        mock_print.assert_called_with("le fichier est vide")

    @patch('builtins.print')
    def test_conformity_dic(self,mock_print):
        load_config("fixtures/pbfile")
        mock_print.assert_called_with("problème de lecture")


    def test_connexion_db(self):
        HOST = "localhost"
        USER = "haine_obs_user"
        PASSWORD = "haine_obs_mdp"
        DATABASE = "haine_obs"
        connex = connexion_db(USER, PASSWORD, HOST, DATABASE)
        self.assertEqual(str(connex), "Engine(postgresql://haine_obs_user:***@localhost/haine_obs)")


    @patch('builtins.print')
    def test_faillure_connexion_db(self, mock_print):
        HOST = "localhost"
        USER = "postgres"
        PASSWORD = "mdp"
        DATABASE = "haine_test"
        connexion_db(USER, PASSWORD, HOST, DATABASE)
        mock_print.assert_called_with("la connexion a echoue")


if __name__ == '__main__':
    unittest.main()







