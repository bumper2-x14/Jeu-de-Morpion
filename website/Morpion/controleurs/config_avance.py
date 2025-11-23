from model.model import get_instances

team_list = get_instances(SESSION['CONNEXION'], 'equipe')

if team_list:
    REQUEST_VARS['team_list'] = team_list