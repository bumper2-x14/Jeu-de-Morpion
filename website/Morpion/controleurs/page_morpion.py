from model.model import get_morpion


morpions = get_morpion(SESSION['CONNEXION'])
print("DEBUG: morpions =", morpions) 
if morpions:
    REQUEST_VARS['morpions'] = morpions
