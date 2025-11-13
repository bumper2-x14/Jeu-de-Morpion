from model.model import get_instances


morpions = get_instances(SESSION['CONNEXION'], "morpion")
if morpions:
    REQUEST_VARS['morpions'] = morpions
