from datetime import datetime
from os import path

SESSION['APP'] = "Jeu de Morpion"
SESSION['BASELINE'] = "..."
SESSION['DIR_HISTORIQUE'] = path.join(SESSION['DIRECTORY'], "historiques")
SESSION['HISTORIQUE'] = dict()
SESSION['CURRENT_YEAR'] = datetime.now().year