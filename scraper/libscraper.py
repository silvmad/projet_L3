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
#    The configuration is in ../config file                                                                #
#    the database model:                                                                                   #
#                                                                                                          #
#    CREATE TABLE messages (                                                                               #
#        ID           SERIAL PRIMARY KEY,                                                                  #
#        Contenu      text NOT NULL,                                                                       #
#        Date         varchar(22) NOT NULL,                                                                #
#        Haineux      boolean default NULL                                                                 #
#    );                                                                                                    #
#                                                                                                          #
#  Twitter Scraper version 1.152: file libscraper.py                                                       #
#            change - small fix for integration                                                            #  
#**********************************************************************************************************#                                   
import os, sys, psycopg2, tweepy

# load config setting
def load_config(dictionnaire, file):
     path1 = os.path.abspath(os.pardir) + "/" + file
     if(os.path.exists(path1)):
          path = path1
     else:
          path = os.path.abspath(os.pardir) + "/../" + file
     try:
          with open(path, 'r') as flux:
               for ligne in flux.readlines():
                    conf = ligne.replace("\n", "").split("\t")
                    try:     
                         dictionnaire[conf[0]] = conf[1]
                    except IndexError:
                         print(f'{path}: Missing information for the field: {ligne}')
     except FileNotFoundError:
          sys.exit(3)

# load search field
def load_field(liste, file):
     path1 = os.path.abspath(os.pardir) + "/" + file
     if(os.path.exists(path1)):
          path = path1
     else:
          path = os.path.abspath(os.pardir) + "/../" + file
     try:
          with open(path, 'r') as flux:
               for ligne in flux:
                    motcle = ligne.replace('\n', '') 
                    if((len(motcle) != 0) and (motcle.count(" ") < len(motcle))):
                         liste.append(motcle)
     except FileNotFoundError:
          sys.exit(4)

# connected to the API?
def check_api_twitter_connexion(api):
     try:
          api.verify_credentials() 
     except:
          sys.exit(1)

#connected to the BDD
def connectbdd(host, database, user, password):
     try:
          c = psycopg2.connect("host=%s dbname=%s user=%s password=%s" % (host, database, user, password))
     except (psycopg2.errors.ConnectionException, psycopg2.errors.SqlclientUnableToEstablishSqlconnection, psycopg2.OperationalError, SyntaxError):
          sys.exit(2)
     return c

#cursor on BDD
def createcursor(con):
     try:
          cur = con.cursor()
     except NameError:
          sys.exit(2)
     return cur

#checks if the configuration respects the limitation
def check_rate(elements, interval, limit):
     return ((900.0/interval) * elements) <= limit

#search and registration request
def scrap(keywords, api, logfile, c, cur, id_erreur, bdd_table, nbr_tweet):
     for element in keywords:
          try:
               for tweet in api.search_tweets(q=element, lang="fr", result_type='recent', count=nbr_tweet , tweet_mode='extended'):
                    tweetsafe = clean_tweet(tweet)
                    cur.execute(f"SELECT count(*) FROM {bdd_table} WHERE Contenu LIKE '{tweetsafe}%' AND Date LIKE '{str(tweet.created_at)}';")
                    duplicate_test = cur.fetchone()
                    if(duplicate_test[0] == 0):
                         scrap_record(duplicate_test, logfile, c, cur, id_erreur, bdd_table, tweet, tweetsafe)
          except tweepy.TweepError:
               sys.exit(1)
#database registration
def scrap_record(duplicate_test, logfile, c, cur, id_erreur, bdd_table, tweet, tweetsafe):
     if(duplicate_test[0] == 0):
          try:
               cur.execute(f"INSERT INTO {bdd_table} (Contenu, Date) VALUES ('{tweetsafe}', '{tweet.created_at}')")
               c.commit()
          except (NameError, psycopg2.errors.InFailedSqlTransaction, psycopg2.errors.NoActiveSqlTransaction):
               c.rollback()
          except tweepy.TweepError:
               id_erreur = closelog(id_erreur, logfile, tweet, tweetsafe)
               sys.exit(1)        
          except:
               id_erreur = closelog(id_erreur, logfile, tweet, tweetsafe)
               sys.exit(6)

# cleanning fuctions
def removeat(mot):
     return  mot.startswith('@')

def clean_tweet(tweet):
     result = ""
     if hasattr(tweet,'retweeted_status'):
          tweetsafe = tweet.retweeted_status.full_text.replace("\n", "")
     else:
          tweetsafe = tweet.full_text.replace("\n", "")  
     tweetsafe = tweetsafe.replace("'", "''")
     for word in tweetsafe.split():
          if not(removeat(word)):
               result = result + word + " "
     return result[0: -1]      

# log functions
def closelog(id_erreur, logfile, tweet, tweetsafe):
     erreur_s = sys.exc_info()
     typerr = u"%s" % (erreur_s[0])
     typerr = typerr[typerr.find("'")+1:typerr.rfind("'")]
     if tweet:
          create_at = tweet.created_at
     else:
          create_at = ""
     logfile.write(f'\t{{\n\t\t"key": {id_erreur},\n\t\t"error": "{typerr}",\n\t\t"date": "{create_at}",\n\t\t"msg": "{tweetsafe}"\n\t}},\n')         
     return (id_erreur + 1)    
