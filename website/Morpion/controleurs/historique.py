from model.model import get_game_hist

historique = get_game_hist(SESSION['CONNEXION'])

REQUEST_VARS['historique'] = historique 
print(historique)