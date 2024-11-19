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
#  Twitter Scraper version 1.152:                                                                          #
#        tested under Ubuntu 20.x                                                                          #
#        dedicated functions are in ./libscraper.py now                                                    # 
#            change - small fix for integration                                                            #
#**********************************************************************************************************#                                   
import tweepy, datetime, time, os , sys
from libscraper import *

#**********************************************************************************************************#                                   
#                                                    Main                                                  #
#**********************************************************************************************************#                                   

# var init
config = {}
keywords = []
status = True
logfile = None
erreur = 0
id_erreur = 1
tweet = ""
tweetsafe = "" 

# load settings
load_config(config, "config")
# load field list
load_field(keywords, "keywords")

# Twitter auth
CONSUMER_KEY =  config.get("T_api_key")
CONSUMER_SECRET = config.get("T_api_secret")
ACCES_TOKEN = config.get("T_api_token")
ACCES_TOKEN_SECRET = config.get("T_api_token_secret")
T_INTERVAL = int(config.get("interval"))
T_RATE = int(config.get("rate_limite"))

# API Twitter
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCES_TOKEN, ACCES_TOKEN_SECRET)
# rate watcher
api = tweepy.API(auth, wait_on_rate_limit=True)#, wait_on_rate_limit_notify=True)
check_api_twitter_connexion(api)

# Postgres connexion
HOST = config.get("Bdd_host")
USER = config.get("Bdd_login")
PASSWORD = config.get("Bdd_secret")
DATABASE = config.get("Bdd")

c = connectbdd(HOST, DATABASE, USER, PASSWORD)
cur = createcursor(c)

#setting for interval
start = round(time.time())
modulo_start = start%T_INTERVAL
nbr_tweet = config.get("nbre_tweet")

#logfile
now = datetime.datetime.utcnow()
logpath = os.path.abspath(os.pardir) + "/scraper"
if os.path.isdir(logpath):
     logname = os.getcwd()+"/log/log"+str(now)+".json"
else:
     logname = os.getcwd()+"/../../scraper/log/log"+str(now)+".json"
logfile = open(logname, 'a')
logfile.write(f'{{"scraplog" : "{now}"\n "record" : [')

# main loop
if not check_rate(len(keywords), T_INTERVAL, T_RATE):
     sys.exit(5)
else:
     while(status):
          if(round(time.time())%T_INTERVAL == modulo_start):
               try:
                    scrap(keywords, api, logfile, c, cur, id_erreur, "messages", nbr_tweet)
                    print("205 new data available")
                    sys.stdout.flush()
               except KeyboardInterrupt:
                    status = False  
          else:
               try:
                    time.sleep(1)
               except KeyboardInterrupt:
                    status = False
               except:
                    id_erreur = closelog(id_erreur, logfile, tweet, tweetsafe)
                    sys.exit(6)

# logfile ending
if not(logfile.closed):
     logfile.write("  ]\n}")
     logfile.close()
     if (id_erreur == 1):
          os.remove(logname)

# clean cursor     
try:
     c.close()
except NameError:
     pass

sys.exit(0)
