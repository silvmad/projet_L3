#! /usr/bin/env python3

"""
analyseur.py : module d'analyse de tweets

Il comporte une interface graphique permettant d'entrer les identifiants de
connexion à la base de données et deux boutons pour lancer et stopper 
l'analyse.
Lors de l'analyse la base de données est interrogée pour récupérer des messages
non encore analysés, les messages sont analysés et la base de données est mise 
à jour en conséquence :
- le champ haineux des messages est mis à true ou false
Puis si le message est haineux :
- des entrées sont ajoutées à la table mot_clé en fonction des mots-clés
    haineux que le message contient.
- une entrée sont ajoutées à la table possède en fonction du type de haine
    concerné.
"""

from torch import device, no_grad, argmax
from torch.cuda import is_available
from torch.nn.functional import softmax
from transformers import CamembertTokenizer, CamembertForSequenceClassification
import psycopg2
import sys, os, time

from PyQt5.QtCore import (QObject, pyqtSignal, QThread)
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFrame, QMessageBox


class MainWindow(QWidget):
    """Classe représentant la fenêtre principale du module d'analyse.
    """
    CONF_FILENAME = "db.conf"
    start_analyse = pyqtSignal()
    
    def __init__(self):
        """Constructeur de la classe MainWindow."""
        super().__init__()

        self.setWindowTitle("Analyseur")

        self.layout = QVBoxLayout(self)
        self.db_layout = QGridLayout()
        self.bt_layout = QHBoxLayout()
        self.line = QFrame()
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.label = QLabel("L'analyseur est prêt à être lancé.", self)
        
        self.layout.addLayout(self.db_layout)
        self.layout.addWidget(self.line)
        self.layout.addWidget(self.label)
        self.layout.addLayout(self.bt_layout)

        self.conf = self.load_config(self.CONF_FILENAME)
        self.hostname = self.conf.get("hostname")
        self.db_name = self.conf.get("db_name")
        self.user_name = self.conf.get("user_name")
        self.user_pw = self.conf.get("user_pw")

        self.ql_hostname = QLineEdit(self.hostname, self)
        self.ql_db_name = QLineEdit(self.db_name, self)
        self.ql_user_name = QLineEdit(self.user_name, self)
        self.ql_user_pw = QLineEdit(self.user_pw, self)

        self.apply_bt = QPushButton("Appliquer")
        
        self.db_layout.addWidget(QLabel("Nom d'hôte"), 0, 0)
        self.db_layout.addWidget(QLabel("Nom de la base de données"), 1, 0)
        self.db_layout.addWidget(QLabel("Nom d'utilisateur"), 2, 0)
        self.db_layout.addWidget(QLabel("Mot de passe utilisateur"), 3, 0)
        self.db_layout.addWidget(self.ql_hostname, 0, 1)
        self.db_layout.addWidget(self.ql_db_name, 1, 1)
        self.db_layout.addWidget(self.ql_user_name, 2, 1)
        self.db_layout.addWidget(self.ql_user_pw, 3, 1)
        self.db_layout.addWidget(self.apply_bt, 4, 1)

        self.start_bt = QPushButton("Lancer l'analyse")
        self.stop_bt = QPushButton("Stopper l'analyse")

        self.bt_layout.addWidget(self.start_bt)
        self.bt_layout.addWidget(self.stop_bt)

        self.apply_bt.clicked.connect(self.apply)
        self.start_bt.clicked.connect(self.analyse)
        self.stop_bt.clicked.connect(self.stop_analyse)

        self.conn = None 
        
        self.analyse_thread = QThread()
        self.analyser = Analyser()
        self.analyser.moveToThread(self.analyse_thread)

        self.analyser.analyse_finished.connect(self.print_end_msg)
        self.start_analyse.connect(self.analyser.analyse)
        self.analyse_thread.start()

        
    def load_config(self, file):
        """Charge les informations de configuration. 
        
        Notamment les identifiants permettant de se connecter à la base de 
        données.
        Arguments :
        file : le fichier contenant les informations.
        Retour :
        Un dictionnaire contenant les informations.
        """
        dic = {}
        try:
            with open(file, "r") as f:
                lines = f.read().splitlines()
                for line in lines:
                    line = line.split('\t')
                    try:
                        dic[line[0]] = line[1]
                    except IndexError:
                        print("Information manquante pour le champ {}".format(line))
                        dic[line[0]] = ""
        except FileNotFoundError:
            print("Impossible de trouver le fichier de configuration")
            sys.exit(1)
        return dic

    def save_config(self):
        """Sauvegarde les informations de configuration.
        
        Les informations de configuration sont enregistrée dans le fichier
        CONF_FILENAME.
        """
        with open(self.CONF_FILENAME, "w") as f:
            for key, val in self.conf.items():
                f.write("{}\t{}\n".format(key, val))

    def db_connect(self, host, db, user, pw):
        """Renvoie une connexion à la base de données.
        
        Arguments :
        host : nom d'hôte.
        db : nom de la base.
        user : nom d'utilisateur.
        pw : mot de passe utilisateur.
        
        Retour :
        Une connexion à la base de données.
        """
        try:
            c = psycopg2.connect(
                "host={} dbname={} user={} password={}".format(
                    host,
                    db,
                    user,
                    pw))
        except (psycopg2.errors.ConnectionException, 
                psycopg2.errors.SqlclientUnableToEstablishSqlconnection, 
                psycopg2.OperationalError, 
                SyntaxError):
            #sys.exit(2) #Connexion impossible
            c = None
        return c

    def apply(self):
        """Applique les identifiants de connexion entrés par l'utilisateur.
        
        Essaie de se connecter à la base de données, puis si la connexion 
        réussit, propose à l'utilisateur d'écrire ces nouveaux identifiants
        dans le fichier de configuration.
        """
        host = self.ql_hostname.text()
        db = self.ql_db_name.text()
        user = self.ql_user_name.text()
        pw = self.ql_user_pw.text()
        c = self.db_connect(host, db, user, pw)
        if (not c):
            QMessageBox.warning(self,
                                "Connexion impossible",
                                "La connexion à la base de données à échoué, "
                                "les données de connexion ne seront pas "
                                "sauvegardées.")
        else:
            ret = QMessageBox.question(self,
                                       "Sauvegarde",
                                       "Les anciennes données de connexion "
                                       "seront écrasées, voulez-vous "
                                       "continuer ?",
                                       QMessageBox.Yes | QMessageBox.No,
                                       QMessageBox.No)
            if (ret == QMessageBox.Yes):
                self.hostname = host
                self.db_name = db
                self.user_name = user
                self.user_pw = pw
                self.conf["hostname"] = host
                self.conf["db_name"] = db
                self.conf["user_name"] = user
                self.conf["user_pw"] = pw
                self.save_config()

    def analyse(self):
        """Slot permettant de lancer l'analyse."""
        if (self.analyser.analyse_running):
            return
        self.analyser.analyse_running = True
        self.conn = self.db_connect(self.hostname, self.db_name, self.user_name, 
                               self.user_pw)
        if (not self.conn):
            QMessageBox.warning(self,
                                "Connexion impossible",
                                "La connexion à la base de données à échoué, "
                                "l'analyse n'a pas pu se lancer.")
            return
        self.analyser.set_conn(self.conn)
        self.label.setText("L'analyse est en cours.")
        self.start_analyse.emit()  
        
    def stop_analyse(self):
        """Slot permettant d'arrêter l'analyse."""
        self.analyser.control["Continue"] = False
        self.analyse_running = False
        self.label.setText("L'analyse est arrêtée.")

        
    def print_end_msg(self):
        """Slot affichant un message si l'analyse s'arrête d'elle-même."""
        self.label.setText("L'analyse est arrêtée.")
        QMessageBox.information(self,
                                "Analyse terminée",
                                "Tous les messages de la base de données sont "
                                "étiquetés, l'analyse s'est arrêtée.")
        

class Analyser(QObject):
    """Classe contenant les fonctions nécessaires à l'analyse.
    
    Ces fonction sont définies comme méthodes d'une classe séparées afin de
    pourvoir être éxécutées dans un QThread par la classe MainWindow.
    """
    
    analyse_finished = pyqtSignal()
    
    def __init__(self):
        """Constructeur de a classe Analyser."""
        super(Analyser, self).__init__()
        self.conn = None
        self.cur = None
        self.type_codes = None
        self.kw = None
        self.control = { "Continue" : True }
        self.analyse_running = False
        
        base_path = os.path.abspath(".")
        path = os.path.abspath(os.path.join(base_path, "models/final_model"))
        # Charger le modèle.
        self.tokenizer = CamembertTokenizer.from_pretrained(path, do_lowercase=False)
        self.classifier = CamembertForSequenceClassification.from_pretrained(path)
        self.device = device('cuda') if is_available() else device('cpu')
        self.classifier.to(self.device)

    def set_conn(self, conn):
        """Setter de l'attribut conn."""
        self.conn = conn
    
    def analyse(self):
        """Méthode contenant la boucle d'analyse."""
        self.cur = self.conn.cursor()
        self.get_type_codes()
        self.get_kw()
        self.control["Continue"] = True
        while(self.control["Continue"]):
            self.cur.execute("select id, contenu from messages where haineux is null order by id limit 100")
            resp = self.cur.fetchall()
            self.parse_resp(resp)
            self.conn.commit()
        self.cur.close()
        self.conn.close()
        self.analyse_running = False
            
    def parse_resp(self, resp):
        """Analyse du retour de la requète sur la base de données."""
        if (len(resp) == 0):
            self.control["Continue"] = False
            self.analyse_finished.emit()
            #time.sleep(10)
        else:
            for msg_id, msg in resp:
                self.parse_msg(msg_id, msg)
                    
    def parse_msg(self, msg_id, msg):
        """Analyse d'un message."""
        label = self.predict(msg)
        if label == 'normal':
            self.set_hateful(msg_id, "false")
        else:
            self.set_hateful(msg_id, "true")
            self.set_type(msg_id, self.type_codes[label])
            self.parse_kw(msg_id, msg)
            
    def parse_kw(self, msg_id, msg):
        """Analyse des mots-clés d'un message."""
        for kw_id, kw in self.kw:
            if kw in msg:
                self.set_kw(msg_id, kw_id)
                    
    def set_hateful(self, msg_id, val):
        """Mise à jour du champ haineux de la table messages."""
        self.cur.execute("update messages set haineux=%s where id=%s;", (val, msg_id))
        
    def set_type(self, msg_id, type_id):
        """Ajout d'entrée à la table possede."""
        self.cur.execute("insert into possede values (%s, %s);", (msg_id, type_id))
        
    def set_kw(self, msg_id, kw_id):
        """Ajout d'entrée à la table contient."""
        self.cur.execute("insert into contient values (%s, %s)", (msg_id, kw_id))
    
    def predict(self, phrase):
        """Prédit le label correspondant à un message."""
        enc = self.tokenizer(phrase, padding=True, truncation=True, max_length=512,
                             return_tensors='pt')
        enc.to(self.device)
        with no_grad():
            outp = self.classifier(**enc)
        pred = softmax(outp.logits, dim=1)
        plabels = argmax(pred, dim=1)
        lab = plabels[0]
        if lab == 0:
            slab = "validisme" 
        elif lab == 1:
            slab = "homophobie"
        elif lab == 2:
            slab = "sexisme"
        elif lab == 3:
            slab = "normal"
        elif lab == 4:
            slab = "racisme"
        return slab
            
    def get_type_codes(self):
        """Obtient les id correspondant aux types de haine."""
        self.type_codes = {}
        self.cur.execute("SELECT * FROM type")
        for t in self.cur:
            self.type_codes[t[1]] = t[0]
    
    def get_kw(self):
        """Obtient les id correspondant aux mots-clés."""
        self.cur.execute("SELECT * FROM mot_clé")        
        self.kw = self.cur.fetchall()
    
    
if __name__ == '__main__':
    app = QApplication([])
    main_window = MainWindow()
    main_window.show()
    app.exec()
