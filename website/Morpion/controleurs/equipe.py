from model.model import get_instances

equipes = get_instances(SESSION['CONNEXION'], "equipe")
if (equipes):
        REQUEST_VARS['equipes'] = equipes
