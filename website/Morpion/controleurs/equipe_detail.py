from model.model import get_instances_by_id, get_equipe_details ,get_team_hist

eq_id = int(GET['id'][0])
selected_equipe = get_instances_by_id(SESSION['CONNEXION'], 'equipe', eq_id)
eq_morpions = get_equipe_details(SESSION['CONNEXION'], eq_id)

REQUEST_VARS['sel_equipe'] = selected_equipe
REQUEST_VARS['eq_morps'] = eq_morpions


team_hist = get_team_hist(SESSION['CONNEXION'], eq_id)
REQUEST_VARS['team_hist'] = team_hist