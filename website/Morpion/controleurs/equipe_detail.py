from model.model import get_instances_by_id, get_equipe_details

eq_id = int(GET['id'][0])
selected_equipe = get_instances_by_id(SESSION['CONNEXION'], 'equipe', eq_id)
eq_morpions = get_equipe_details(SESSION['CONNEXION'], eq_id)

REQUEST_VARS['sel_equipe'] = selected_equipe
REQUEST_VARS['eq_morps'] = eq_morpions