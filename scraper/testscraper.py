#**********************************************************************************************************#
#  This program was written by Mickael D. Pernet on 05/31/2021                                             #
#  For second year computer science course: program realization                                            #
#                                                                                                          #
#  This scrape program requires the following libraries                                                    #
#              - Tweepy for the Twitter API: https://www.tweepy.org/                                       #
#              - psycopg2 for postgres database: https://pypi.org/project/psycopg2/                        #
#                                                                                                          #
#  It also requires permission to use the Twitter API:  https://developer.twitter.com/en                   #
#                                                                                                          #
#    The configuration is in ../config.sys file                                                            #
#    the database model:                                                                                   #
#                                                                                                          #
#    CREATE TABLE messages (                                                                               #
#        ID           SERIAL PRIMARY KEY,                                                                  #
#        Contenu      text NOT NULL,                                                                       #
#        Date         varchar(22) NOT NULL,                                                                #
#        Haineux      boolean default NULL                                                                 #
#    );                                                                                                    #
#                                                                                                          #
#  Twitter Scraper version 1.15: file testscraper.py:                                                      #
#                   test use as part of the integration                                                    #
#                   improvement:                                                                           #
#                       test double with use of mocks, stubs and fakes instead of real external dependency #
#**********************************************************************************************************#                                   
import unittest
import os, tweepy, random
from tweepy import api 
from libscraper import *

class TestScraper(unittest.TestCase):

    def test_loadconfig(self):
        file = "config.sys"
        path = os.path.abspath(os.pardir) + "/" + file
        if(os.path.isfile(path)):
            config = {}
            load_config(config, file)
            self.assertTrue("T_api_key" in config.keys())            
            self.assertTrue(len(config.get("T_api_key")) > 0)
            self.assertTrue("T_api_secret" in config.keys())
            self.assertTrue(len(config.get("T_api_key")) > 0)
            self.assertTrue("T_api_token" in config.keys())
            self.assertTrue(len(config.get("T_api_key")) > 0)
            self.assertTrue("T_api_token_secret" in config.keys())
            self.assertTrue(len(config.get("T_api_key")) > 0)
            self.assertTrue("Bdd_host" in config.keys())
            self.assertTrue(len(config.get("T_api_key")) > 0)
            self.assertTrue("Bdd_login" in config.keys())
            self.assertTrue(len(config.get("T_api_key")) > 0)
            self.assertTrue("Bdd_secret" in config.keys())
            self.assertTrue(len(config.get("T_api_key")) > 0)
            self.assertTrue("Bdd" in config.keys())
            self.assertTrue(len(config.get("T_api_key")) > 0)
            self.assertTrue("langue" in config.keys())
            self.assertTrue(len(config.get("T_api_key")) > 0)
            self.assertTrue("nbre_tweet" in config.keys())
            self.assertTrue(len(config.get("T_api_key")) > 0)
            self.assertTrue("max_tweet" in config.keys())
            self.assertTrue(len(config.get("T_api_key")) > 0)
            self.assertTrue("rate_limite" in config.keys())
            self.assertTrue(len(config.get("T_api_key")) > 0)
            self.assertTrue("interval" in config.keys())
            with self.assertRaises(SystemExit) as errortest:
                load_config(config, "test.sys")
                self.assertEqual(errortest.exception.code, 3)   
        else:
            print(f'\nerror\tfile {path} is missing for test_loadconfig()\n')
      

    def test_loadfield(self):
        list_test = []
        path = os.path.abspath(os.pardir) + "/goliste.txt"
        if(os.path.isfile(path)):
            load_field(list_test, "goliste.txt")
            self.assertTrue(len(list_test) > 0)
            with self.assertRaises(SystemExit) as errortest:
                load_field(list_test, "test.txt")
                self.assertEqual(errortest.exception.code, 4)
        else:
            print(f'\nerror\tfile {path} is missing for test_loadconfig()\n') 


    def test_check_api_twitter_connexion(self):
        path = os.path.abspath(os.pardir) + "/config.sys"
        if(os.path.isfile(path)):
            config = {}
            load_config(config, "config.sys")
            auth = tweepy.OAuthHandler(config.get("T_api_key"), config.get("T_api_secret"))
            self.assertTrue(auth.set_access_token(config.get("T_api_token"), config.get("T_api_token_secret")) == None)
            with self.assertRaises(SystemExit) as errortest:
                check_api_twitter_connexion(api)
                self.assertEqual(errortest.exception.code, 1)
        else:
            print(f'\nerror\tfile {path} is missing for  test_check_APITwitter_connecion())\n')

    def test_connectbdd_n_createcursor(self):
        path = os.path.abspath(os.pardir) + "/config.sys"
        if(os.path.isfile(path)):
            config = {}
            load_config(config, "config.sys")
            self.assertTrue(connectbdd(config.get("Bdd_host"), config.get("Bdd"), config.get("Bdd_login"), config.get("Bdd_secret")))
            self.assertTrue(createcursor(connectbdd(config.get("Bdd_host"), config.get("Bdd"), config.get("Bdd_login"), config.get("Bdd_secret"))))
            with self.assertRaises(SystemExit) as errortest:
                connectbdd(config.get("Bdd_host"), config.get("Bdd"), config.get("Bdd_login"), "test")
                self.assertEqual(errortest.exception.code, 2)
            with self.assertRaises(SystemExit) as errortest:
                createcursor(connectbdd(config.get("Bdd_host"), config.get("Bdd"), config.get("Bdd_login"), "test"))
                self.assertEqual(errortest.exception.code, 2)
        else:
            print(f'\nerror\tfile {path} is missing for test_connectbdd())\n')

    def test_chek_rate(self):
        #self.assertTrue(check_rate(keywords, interval, limit))
        self.assertTrue(check_rate(random.randint(1, 450), 900, 450))
        self.assertTrue(check_rate(random.randint(1, 450), 900, 450))
        self.assertTrue(check_rate(random.randint(1, 450), 900, 450))
        self.assertTrue(check_rate(450, random.randint(900, 1800), 450))
        self.assertTrue(check_rate(450, random.randint(900, 1800), 450))
        self.assertTrue(check_rate(450, random.randint(900, 1800), 450))
        self.assertFalse(check_rate(random.randint(451, 900), 900, 450))
        self.assertFalse(check_rate(random.randint(451, 900), 900, 450))
        self.assertFalse(check_rate(random.randint(451, 900), 900, 450))
        self.assertFalse(check_rate(450, random.randint(1, 899), 450))
        self.assertFalse(check_rate(450, random.randint(1, 899), 450))
        self.assertFalse(check_rate(450, random.randint(1, 899), 450))

    def test_removeat(self):
        self.assertTrue(removeat("test") == False)
        self.assertTrue(removeat("test@") == False)
        self.assertTrue(removeat("te@st") == False)
        self.assertTrue(removeat("@test") == True)

#it's a test
if __name__ == '__main__':
    unittest.main()