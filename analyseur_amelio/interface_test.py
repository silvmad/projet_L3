#! /usr/bin/env python3

from torch import device, no_grad, argmax
from torch.cuda import is_available
from torch.nn.functional import softmax
from transformers import CamembertTokenizer, CamembertForSequenceClassification
try:
    from PySide6.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QLineEdit, QPushButton
    from PySide6.QtGui import QShortcut, QKeySequence
except ImportError:
    from PyQt5.QtWidgets import QApplicaiton, QWidget, QGridLayout, QLabel, QLineEdit, QPushButton
    from PyQt5.QtGui import QShortcut, QKeySequence
import os
import sys

class MainWindows(QWidget):
    def __init__(self):
        super().__init__()
        
        # Initialisation.
        self.layout = QGridLayout(self)
        self.intro = QLabel("Entrez le message à vérifier :")
        self.edit = QLineEdit()
        self.buttonV = QPushButton("vérifier")
        self.resultat = QLabel("")

        # Ajout.
        self.layout.addWidget(self.intro, 0, 0, 1, 1)
        self.layout.addWidget(self.edit, 1, 0, 1, 1)
        self.layout.addWidget(self.buttonV, 1, 2, 1, 1)
        self.layout.addWidget(self.resultat, 2, 0, 1, 1)

        # Window parameters.
        self.setWindowTitle("Détecteur de haine")
        self.setFixedSize(500, 150)
        
        # Chemin vers le modèle
        #try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            #base_path = sys._MEIPASS
        #    base_path = getattr(sys, '_MEIPASS', path.abspath(os.path.dirname(__file__)))
        #except Exception:
        base_path = os.path.abspath(".")
        path = os.path.abspath(os.path.join(base_path, "models/"))
        # Charger le modèle.
        self.tokenizer = CamembertTokenizer.from_pretrained(path + "/tweetbert", do_lowercase=False)
        self.classifier = CamembertForSequenceClassification.from_pretrained(path + "/final_model")
        self.device = device('cuda') if is_available() else device('cpu')
        self.classifier.to(self.device)
        
        QShortcut(QKeySequence("return"), self.edit, self.predict)
        self.buttonV.clicked.connect(self.predict) 
    
    def predict(self):
        """
        Effectue une prédiction sur le phrase dans le QLineEdit self.edit.
        Écrit le résultat dans le Label self.resultat.
        """
        phrase = self.edit.text()
        if (phrase == ""):
            self.resultat.setText("")
            return
        enc = self.tokenizer(phrase, padding=True, truncation=True, max_length=512, return_tensors='pt')
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
        self.resultat.setText("Résultat :\t {}\n(validisme {:.2f}% / homophobie {:.2f}% / sexisme {:.2f}%\n / normal {:.2f}% / racisme {:.2f}%)".format(slab, pred[0, 0]*100, pred[0, 1]*100, pred[0, 2]*100, pred[0, 3]*100, pred[0, 4]*100))

if __name__ == '__main__':
    app = QApplication([])
    main_window = MainWindows()
    main_window.show()
    app.exec()
    
