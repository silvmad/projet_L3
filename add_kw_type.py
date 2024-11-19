import psycopg2
import sys

argv = sys.argv
if len(argv) != 5:
    print("usage : ./{} hostname, db_name, user_name, user_password".format(argv[0]))
    sys.exit(1)
    
host = argv[1]
db = argv[2]
user = argv[3]
pw = argv[4]

c = psycopg2.connect("host={} dbname={} user={} password={}".format(host, db, user, pw))
if (not c):
    print("Impossible de se connecter à la base de données avec les identifiants fournis.")
    sys.exit(1)
    
cur = c.cursor()

try:
    with open("keywords", "r") as f:
        kw = f.read().splitlines()
except FileNotFoundError:
    print("Impossible d'ouvrir le fichier keywords.")
    sys.exit(1)

# Ajout des types.
for t in ["racisme", "validisme", "homophobie", "sexisme"]:
    cur.execute("INSERT INTO type(nom_type) VALUES (%s)", (t, ))
    
# Ajout des mots-clé.
for k in kw:
    cur.execute("INSERT INTO mot_clé(mot) VALUES (%s)", (k, ))

c.commit()
